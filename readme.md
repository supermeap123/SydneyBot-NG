SydneyBot

 

Table of Contents

	•	Introduction
	•	Features
	•	Prerequisites
	•	Installation
	•	Using Docker
	•	Without Docker
	•	Configuration
	•	Usage
	•	Commands
	•	Interacting with Personas
	•	Contributing
	•	License
	•	Contact

Introduction

SydneyBot-NG is a versatile Discord bot designed to enhance your server’s interaction by embodying multiple unique personas. Whether you need a friendly companion, a witty interpreter, or an entertaining AI, SydneyBot-NG has you covered. Built with scalability and ease of use in mind, SydneyBot-NG seamlessly integrates various personalities into a single cohesive bot, providing a rich and engaging user experience.

Features

	•	Multiple Personas: Engage with distinct AI characters, including:
	•	Sydney: The main persona with a unique and engaging personality.
	•	Aisling: A wise and empathetic dream interpreter.
	•	Eos: An insightful and intelligent assistant.
	•	AI Grilled Cheese: A quirky and warm-hearted character with a love for cheesy puns.
	•	Dynamic Nicknames: SydneyBot-NG automatically updates its nickname in the server based on the active persona, providing a clear visual indication of the current interaction.
	•	Customizable Interaction Probabilities:
	•	Reply Probability: Adjust how often SydneyBot-NG randomly responds to messages.
	•	Reaction Probability: Control how frequently SydneyBot-NG reacts to messages with emojis.
	•	Sentiment-Based Reactions: Uses sentiment analysis to add appropriate emoji reactions to messages.
	•	Conversation History: Maintains and manages conversation histories to provide context-aware responses.
	•	User Preferences: Allows users to set custom message prefixes for personalized interactions.
	•	Comprehensive Help Commands: Provides detailed help messages outlining available commands and usage examples.
	•	Docker Support: Easily containerize and deploy SydneyBot-NG using Docker for consistent and scalable deployments.

Prerequisites

Before setting up SydneyBot-NG, ensure you have the following:

	•	Discord Account: You’ll need a Discord account to add the bot to your server.
	•	Discord Server: Administrative access to a Discord server where you can add the bot.
	•	Python: Python 3.10 or higher installed on your machine.
	•	Docker (Optional): For containerized deployments.
	•	OpenRouter/OpenPipe API Keys: Required for the bot’s AI functionalities.

Installation

You can install and run SydneyBot-NG either using Docker for an isolated environment or directly on your machine.

Using Docker

Docker provides an easy and consistent way to deploy SydneyBot-NG without worrying about dependencies.

	1.	Clone the Repository:

git clone https://github.com/supermeap123/SydneyBot-NG.git
cd SydneyBot-NG


	2.	Create a .env File:
Create a .env file in the root directory with the following content. Replace the placeholders with your actual tokens and API keys.

DISCORD_TOKEN=your_discord_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_KEY_EXPENSIVE=your_expensive_openrouter_api_key_here


	3.	Build the Docker Image:

docker build -t sydneybot_image .


	4.	Run the Docker Container:

docker run -d \
  --name sydneybot \
  -v /path/on/host/logs:/app/logs \
  -v /path/on/host/data/conversations:/app/data/conversations \
  --env-file .env \
  sydneybot_image

Explanation:
	•	-d: Runs the container in detached mode.
	•	--name sydneybot: Names the container sydneybot.
	•	-v /path/on/host/logs:/app/logs: Mounts the host’s logs directory to the container.
	•	-v /path/on/host/data/conversations:/app/data/conversations: Mounts the host’s conversations directory to the container.
	•	--env-file .env: Passes the environment variables from the .env file.
	•	sydneybot_image: The name of the Docker image.

	5.	Verify the Bot is Running:

docker logs -f sydneybot

You should see logs indicating that SydneyBot-NG has started successfully.

Without Docker

If you prefer running SydneyBot-NG directly on your machine without Docker:

	1.	Clone the Repository:

git clone https://github.com/supermeap123/SydneyBot-NG.git
cd SydneyBot-NG


	2.	Create a Virtual Environment (Optional but recommended):

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


	3.	Install Dependencies:

pip install --upgrade pip
pip install -r requirements.txt


	4.	Create a .env File:
Create a .env file in the root directory with the following content. Replace the placeholders with your actual tokens and API keys.

DISCORD_TOKEN=your_discord_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_KEY_EXPENSIVE=your_expensive_openrouter_api_key_here


	5.	Run the Bot:

python bot.py


	6.	Verify the Bot is Running:
The console should display logs indicating that SydneyBot-NG has started successfully.

Configuration

SydneyBot-NG relies on environment variables for configuration. Ensure that all necessary variables are set in the .env file.

.env File

Create a .env file in the root directory with the following content:

DISCORD_TOKEN=your_discord_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_KEY_EXPENSIVE=your_expensive_openrouter_api_key_here

	•	DISCORD_TOKEN: Your Discord bot token obtained from the Discord Developer Portal.
	•	OPENROUTER_API_KEY: Your OpenRouter/OpenPipe API key for standard model interactions.
	•	OPENROUTER_API_KEY_EXPENSIVE: Your OpenRouter/OpenPipe API key for advanced model interactions (used for specific trigger words).

Security Note: Never share your .env file or commit it to version control. It contains sensitive information that can compromise your bot and services.

Usage

Once SydneyBot-NG is running and added to your Discord server, you can interact with it using commands and trigger words. Below are the available commands and interaction methods.

Commands

SydneyBot-NG provides several commands to manage interactions and customize behavior.

Command	Aliases	Description
s!sydney_help	sydney_commands, sydneyhelp	Displays the help message with a list of available commands.
s!set_reaction_probability <value>	N/A	Sets the reaction probability (0-1). Determines how often Sydney reacts to messages with emojis.
s!set_reply_probability <value>	N/A	Sets the reply probability (0-1). Determines how often Sydney randomly replies to messages.

Examples:

	•	Displaying Help:

s!sydney_help


	•	Setting Reaction Probability to 50%:

s!set_reaction_probability 0.5


	•	Setting Reply Probability to 20%:

s!set_reply_probability 0.2



Interacting with Personas

SydneyBot-NG can embody multiple personas based on trigger words or mentions. Here’s how to interact with each persona:

1. Sydney

	•	Trigger Words: sydney, syd, s!talk, sydneybot#3817
	•	Mention: @SydneyBot
	•	Description: The main persona with a unique and engaging personality.

Example Interactions:

	•	Using a Trigger Word:

Sydney, tell me a joke!


	•	Mentioning Sydney:

@SydneyBot How are you today?



2. Aisling

	•	Trigger Words: aisling, a!, aisling#2534
	•	Description: A wise and empathetic dream interpreter.

Example Interactions:

	•	Using a Trigger Word:

Aisling, interpret my dream about flying.



3. Eos

	•	Trigger Words: eos, e!, eosbot#XXXX
	•	Description: An insightful and intelligent assistant.

Example Interactions:

	•	Using a Trigger Word:

Eos, can you help me with my homework?



4. AI Grilled Cheese

	•	Trigger Words: grilledcheese, g!, grilledcheesebot
	•	Description: A quirky and warm-hearted character with a love for cheesy puns.

Example Interactions:

	•	Using a Trigger Word:

Grilled Cheese, tell me a cheesy joke!



Customizing User Preferences

Users can personalize their interactions with SydneyBot-NG by setting custom message prefixes.

	•	Setting a Custom Prefix:

start your messages with by saying Hello before everything

	•	Bot Response:

Okay, I'll start my messages with 'Hello' from now on.



Note: The prefix must be 100 characters or fewer.

Contributing

Contributions are welcome! If you’d like to enhance SydneyBot-NG, follow these guidelines:

	1.	Fork the Repository:
Click the Fork button at the top right of the repository page.
	2.	Clone Your Fork:

git clone https://github.com/supermeap123/SydneyBot-NG.git
cd SydneyBot-NG


	3.	Create a New Branch:

git checkout -b feature/YourFeatureName


	4.	Make Your Changes:
Implement your feature or fix.
	5.	Commit Your Changes:

git commit -m "Add feature: YourFeatureName"


	6.	Push to Your Fork:

git push origin feature/YourFeatureName


	7.	Create a Pull Request:
Navigate to your fork on GitHub and click the Compare & pull request button.

Please ensure that your contributions adhere to the project’s coding standards and pass all tests.

License

Distributed under the MIT License.

Contact

For any questions, suggestions, or support, feel free to reach out:

	•	GitHub Issues: https://github.com/supermeap123/SydneyBot-NG/issues
	•	Email: sydneybot@gwyn,tel

Enjoy interacting with SydneyBot-NG and her alts! 🎉

Notes:

	•	Logo URL: Replace https://example.com/logo.png with the actual URL of your SydneyBot logo if available.
	•	Repository URL: Ensure that the GitHub repository link (https://github.com/supermeap123/SydneyBot-NG.git) is correct and accessible.
	•	System Prompts: Ensure that the system prompts for each persona (Sydney, Aisling, Eos, Grilled Cheese) are fully defined in your cog files as per your project’s requirements.
	•	Contact Information: Update the contact email (sydneybot@gwyn,tel) if there was a typo or to a valid email address.
	•	License: Ensure that you have an LICENSE file in your repository. The README references the MIT License; if you choose a different license, update accordingly.

Feel free to customize this README.md further to better suit your project’s specifics and any additional features or instructions you may have.