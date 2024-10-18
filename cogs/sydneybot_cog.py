# cogs/sydneybot_cog.py
import discord
from discord.ext import commands, tasks
import time
import asyncio
import random
import re
from config import logger
from helpers import (
    contains_trigger_word,
    is_bot_mentioned,
    random_chance,
    replace_usernames_with_mentions,
    replace_ping_with_mention,
    replace_name_exclamation_with_mention,
    is_valid_prefix,
    get_system_prompt,
    get_reaction_system_prompt,
    is_refusal
)
from database import (
    load_user_preference,
    save_user_preference,
    backup_database,
    load_probabilities,
    save_probabilities
)
from openapi import get_valid_response, get_reaction_response

class SydneyBotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_histories = {}
        self.MAX_HISTORY_LENGTH = 50
        self.start_time = time.time()
        self.recent_messages = {}  # To track recent messages and their authors
        self.temperature = 0.1777  # Default temperature

        # Define personas with their respective trigger words and system prompts
        self.personas = {
            "sydney": {
                "trigger_words": ["sydney", "syd", "s!talk", "sydneybot#3817"],
                "system_prompt_func": lambda user, server, channel: get_system_prompt(user, server, channel)
            },
            "aisling": {
                "trigger_words": ["aisling", "a!", "aisling#2534"],
                "system_prompt_func": lambda user, server, channel: """Meet Aisling (pronounced ASH-ling), a wise and empathetic dream interpreter with an otherworldly aura. [Truncated for brevity]"""
            },
            "eos": {
                "trigger_words": ["eos", "e!", "eosbot#XXXX"],
                "system_prompt_func": lambda user, server, channel: """You are Eos... [Truncated for brevity]"""
            },
            "grilled_cheese": {
                "trigger_words": ["grilledcheese", "g!", "grilledcheesebot"],
                "system_prompt_func": lambda user, server, channel: """Meet AI Grilled Cheese... [Truncated for brevity]"""
            }
        }

        self.update_presence.start()

    def cog_unload(self):
        self.update_presence.cancel()

    @tasks.loop(minutes=5)
    async def update_presence(self):
        """Update the bot's presence/status periodically."""
        statuses = [
            discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} servers"),
            discord.Activity(type=discord.ActivityType.listening, name=f"{len(set(self.bot.get_all_members()))} users"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{sum(len(channels) for channels in self.conversation_histories.values())} active chats"),
            discord.Activity(type=discord.ActivityType.playing, name="with AI conversations"),
            discord.Activity(type=discord.ActivityType.watching, name=f"Uptime: {str(datetime.timedelta(seconds=int(time.time() - self.start_time)))}"),
            discord.Activity(type=discord.ActivityType.listening, name="s!sydney_help"),
        ]
        status = random.choice(statuses)
        try:
            await self.bot.change_presence(activity=status)
        except Exception as e:
            logger.error(f"Error updating presence: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages and determine if a response or reaction is needed."""
        if message.author == self.bot.user:
            return

        # Process commands first
        await self.bot.process_commands(message)

        # Check if the message is a command and return if it is
        if message.content.startswith(tuple([f"{cmd} " for cmd in self.bot.command_prefix])):
            return

        logger.debug(f"Received message: {message.content}")

        is_dm = isinstance(message.channel, discord.DMChannel)
        guild_id = "DM" if is_dm else str(message.guild.id)
        channel_id = message.channel.id

        # Load probabilities for the guild and channel
        reply_probability, reaction_probability = load_probabilities(guild_id, channel_id)

        # Initialize conversation history for guild and channel if not present
        if guild_id not in self.conversation_histories:
            self.conversation_histories[guild_id] = {}

        if channel_id not in self.conversation_histories[guild_id]:
            self.conversation_histories[guild_id][channel_id] = []

        role = "assistant" if message.author == self.bot.user else "user"
        content = message.clean_content

        if role == "user":
            content = f"{message.author.display_name}: {content}"

        # Update user preferences based on instructions
        if role == "user":
            # Check for instruction to start messages with a prefix
            match = re.search(r'start your messages with(?: that)? by saying (.+?) before everything', content, re.IGNORECASE)
            if match:
                prefix = match.group(1).strip()
                if is_valid_prefix(prefix):
                    save_user_preference(message.author.id, prefix)
                    await message.channel.send(f"Okay, I'll start my messages with '{prefix}' from now on.")
                else:
                    await message.channel.send("Sorry, that prefix is invalid or too long.")

        self.conversation_histories[guild_id][channel_id].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

        if len(self.conversation_histories[guild_id][channel_id]) > self.MAX_HISTORY_LENGTH:
            self.conversation_histories[guild_id][channel_id] = self.conversation_histories[guild_id][channel_id][-self.MAX_HISTORY_LENGTH:]

        # Track recent messages asynchronously
        if channel_id not in self.recent_messages:
            self.recent_messages[channel_id] = []
        self.recent_messages[channel_id].append((message.author.id, time.time()))

        # Clean up old messages
        self.recent_messages[channel_id] = [
            (author_id, timestamp) for author_id, timestamp in self.recent_messages[channel_id]
            if time.time() - timestamp < 5
        ]

        # Check if another bot has replied recently
        if any(author_id != message.author.id and author_id != self.bot.user.id for author_id, _ in self.recent_messages[channel_id]):
            return

        # Determine which persona to respond as
        persona_key = None
        use_expensive_model = False

        for key, persona in self.personas.items():
            if is_bot_mentioned(message, self.bot.user) and key == "sydney":
                persona_key = key
                break
            elif contains_trigger_word(message.content, persona["trigger_words"]):
                persona_key = key
                if key == "sydney" and "xxx" in message.content.lower():
                    use_expensive_model = True
                break

        if is_dm:
            # Default to Sydney in DMs
            persona_key = "sydney"

        if not persona_key and not random_chance(reply_probability):
            # Decide not to respond
            return

        if persona_key:
            should_respond = True
        else:
            should_respond = random_chance(reply_probability)

        if should_respond:
            await self.handle_response(message, persona_key, use_expensive_model)

        # Reaction handling
        if role == "user" and random_chance(reaction_probability):
            await self.handle_reaction(message)

    async def handle_response(self, message, persona_key, use_expensive_model):
        """Handle generating and sending a response based on the persona."""
        async with message.channel.typing():
            # Build the system prompt
            if persona_key and persona_key in self.personas:
                system_prompt = self.personas[persona_key]["system_prompt_func"](message.author.display_name, message.guild.name if message.guild else "DM", message.channel.name)
            else:
                system_prompt = get_system_prompt(message.author.display_name, message.guild.name if message.guild else "DM", message.channel.name)

            messages = [{"role": "system", "content": system_prompt}]
            # Include the conversation history
            messages.extend(self.conversation_histories[message.guild.id if message.guild else "DM"][message.channel.id])

            tags = {
                "user_id": str(message.author.id),
                "channel_id": str(message.channel.id),
                "server_id": str(message.guild.id) if message.guild else "DM",
                "interaction_type": "trigger_chat",
                "prompt_id": "sydney_v1.0"
            }

            try:
                response = await get_valid_response(
                    messages, 
                    tags, 
                    initial_temperature=self.temperature, 
                    use_expensive_model=use_expensive_model
                )

                # Extract custom name if present
                custom_name_match = re.match(r"^(.+?):\s*(.*)$", response)
                custom_name = custom_name_match.group(1) if custom_name_match else None
                response_content = custom_name_match.group(2) if custom_name_match else response

                # Get user preferences
                message_prefix = load_user_preference(message.author.id)

                # Prepend message prefix if any
                if message_prefix:
                    response_content = f"{message_prefix} {response_content}"

                # Replace placeholders and usernames with mentions
                if not isinstance(message.channel, discord.DMChannel):
                    response_content = replace_usernames_with_mentions(response_content, message.guild)
                    response_content = replace_ping_with_mention(response_content, message.author)
                    response_content = replace_name_exclamation_with_mention(response_content, message.author)

                # Truncate response if it exceeds Discord's limit
                if len(response_content) > 2000:
                    response_content = response_content[:1997] + '...'

                # Use Discord's reply feature
                await message.reply(response_content, mention_author=False)

                # Update conversation history with assistant's response
                self.conversation_histories[message.guild.id if message.guild else "DM"][message.channel.id].append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": time.time()
                })

                if len(self.conversation_histories[message.guild.id if message.guild else "DM"][message.channel.id]) > self.MAX_HISTORY_LENGTH:
                    self.conversation_histories[message.guild.id if message.guild else "DM"][message.channel.id] = self.conversation_histories[message.guild.id if message.guild else "DM"][message.channel.id][-self.MAX_HISTORY_LENGTH:]

                # Backup the database after changes
                backup_database()

            except Exception as e:
                await message.reply("Sorry, I encountered an error while processing your request.")
                logger.error(f"Error processing message from {message.author}: {e}")

    async def handle_reaction(self, message):
        """Handle adding a reaction to the message based on sentiment."""
        try:
            # Prepare the system prompt and user message
            system_prompt = get_reaction_system_prompt()
            user_message = message.clean_content

            # Build the messages for the API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Make the API call to get the reaction
            reaction = await get_reaction_response(messages)

            # Add the reaction to the message
            if reaction:
                await message.add_reaction(reaction.strip())
            else:
                logger.debug("No suitable reaction found.")
        except discord.HTTPException as e:
            logger.error(f"Failed to add reaction: {e}")
        except Exception as e:
            logger.error(f"Error adding reaction to message from {message.author}: {e}")

    # Commands

    @commands.command(name='sydney_help', aliases=['sydney_commands', 'sydneyhelp'])
    async def sydney_help(self, ctx):
        """Displays the help message with a list of available commands."""
        embed = discord.Embed(
            title="SydneyBot Help",
            description="Here are the commands you can use with SydneyBot and her alts:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="General Commands",
            value=(
                "**s!sydney_help**\n"
                "Displays this help message.\n\n"
                "**s!set_reaction_probability <value>**\n"
                "Sets the reaction probability (0-1). Determines how often Sydney reacts to messages with emojis.\n\n"
                "**s!set_reply_probability <value>**\n"
                "Sets the reply probability (0-1). Determines how often Sydney randomly replies to messages.\n"
            ),
            inline=False
        )
        embed.add_field(
            name="Interaction with Sydney",
            value=(
                "Sydney will respond to messages that mention her or contain trigger words.\n"
                "She may also randomly reply or react to messages based on the set probabilities.\n"
                "To get Sydney's attention, you can mention her, use one of her trigger words, or reply to one of her messages.\n"
            ),
            inline=False
        )
        embed.add_field(
            name="Examples",
            value=(
                "- **Mentioning Sydney:** `@SydneyBot How are you today?`\n"
                "- **Using a trigger word:** `Sydney, tell me a joke!`\n"
                "- **Replying to Sydney:** *(reply to one of her messages)* `That's interesting! Tell me more.`\n"
                "- **Setting reaction probability:** `s!set_reaction_probability 0.5`\n"
                "- **Setting reply probability:** `s!set_reply_probability 0.2`\n"
            ),
            inline=False
        )
        embed.set_footer(text="Feel free to reach out if you have any questions!")
        await ctx.send(embed=embed)

    @sydney_help.error
    async def sydney_help_error(self, ctx, error):
        logger.exception(f"Error in sydney_help command: {error}")
        await ctx.send("An error occurred while displaying the help message.")

    @commands.command(name='set_reaction_probability')
    async def set_reaction_probability(self, ctx, value: float):
        """Set the reaction probability (0-1)."""
        if 0 <= value <= 1:
            guild_id = str(ctx.guild.id) if ctx.guild else "DM"
            channel_id = ctx.channel.id
            save_probabilities(guild_id, channel_id, reaction_probability=value)
            await ctx.send(f"Reaction probability set to {value * 100}%.")
        else:
            await ctx.send("Please enter a value between 0 and 1.")

    @set_reaction_probability.error
    async def set_reaction_probability_error(self, ctx, error):
        logger.exception(f"Error in set_reaction_probability command: {error}")
        await ctx.send("Invalid input. Please enter a valid number between 0 and 1.")

    @commands.command(name='set_reply_probability')
    async def set_reply_probability(self, ctx, value: float):
        """Set the reply probability (0-1)."""
        if 0 <= value <= 1:
            guild_id = str(ctx.guild.id) if ctx.guild else "DM"
            channel_id = ctx.channel.id
            save_probabilities(guild_id, channel_id, reply_probability=value)
            await ctx.send(f"Reply probability set to {value * 100}%.")
        else:
            await ctx.send("Please enter a value between 0 and 1.")

    @set_reply_probability.error
    async def set_reply_probability_error(self, ctx, error):
        logger.exception(f"Error in set_reply_probability command: {error}")
        await ctx.send("Invalid input. Please enter a valid number between 0 and 1.")

    # Additional commands for managing personas can be added here

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, I didn't recognize that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Please check the command usage.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument type. Please check the command usage.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again after {round(error.retry_after, 2)} seconds.")
        else:
            await ctx.send("An error occurred while processing the command.")
            logger.error(f"Error processing command from {ctx.author}: {error}", exc_info=True)

def setup(bot):
    bot.add_cog(SydneyBotCog(bot))