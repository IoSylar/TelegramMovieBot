import json

from utils.utils import get_movies
import logging
import pathlib
import os
import telebot
import click
from providers.rag import RAGProvider
from prompts.reccommendation import RecommendationPrompt
from prompts.movie_extraction import MovieExtraction
os.environ["OPENAI_API_KEY"] = 'insert key here'
os.environ["TELEGRAM_BOT_TOKEN"] = "insert key here"
import requests
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  level=logging.INFO)

DATABASE = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Ciao! Sono il bot che ti suggerirà il film da vedere stasera! Scrivi /query seguito dal genere, da un film già visto, dal cast.\n\n Così da poterti consigliare un bel film!\n\n")



async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):

  result = query_movie(str(update.message.text))

  await context.bot.send_message(chat_id=update.effective_chat.id, text=str(result))

def call_streaming_API(title:str, output_language:str,show_type:"all",country:str="IT"):

    url = "https://streaming-availability.p.rapidapi.com/search/title"

    querystring = {"country": country, "title": title, "output_language": output_language, "show_type": show_type}

    headers = {
        "X-RapidAPI-Key": "insert key here",
        "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    parsed_data = response.json()
    if 'result' in parsed_data and parsed_data['result']:
        first_item = parsed_data['result'][0]
        # Check if 'streamingInfo' key exists and 'it' key exists within it
        if 'streamingInfo' in first_item and 'it' in first_item['streamingInfo']:
            # Access the link if it exists
            video_link = first_item['streamingInfo']['it'][0]['link']
            print("Video Link:", video_link)
        else:
            print("No streaming information available for:", first_item['title'])
            video_link = None

    return video_link


def query_movie(query_text:str):

    provider = RAGProvider(api_key = os.environ["OPENAI_API_KEY"])
    prompt = RecommendationPrompt(details = query_text)

    recommendations = provider.query(prompt = prompt)
    prompt_movie_extraction = MovieExtraction(input_text=str(recommendations))
    movie_list = provider.query_llm(prompt=prompt_movie_extraction)

    movie_string = str(movie_list)
    movie_list = movie_string.strip("[]").split(", ")
    array_movie = movie_list

    link_list = dict()
    for title in array_movie:
        print("call "+title)
        value_from_api = call_streaming_API(title, output_language="en", show_type="all", country="IT")
        if value_from_api is not None:
            link_list.update({title: str(value_from_api)})

    result = str(recommendations)
    links = ""
    for key, value in link_list.items():
        links = links +"Movie: "+str(key) +" Streaming on: " +str(value) +"\n\n"

    final_output = result + "\n\n" + links
    return final_output


def create_index(input_path: str, api_key: str):
    """
    Creates a VectorDB Index based on Movie Metadata in JSON.

    Params:
        input_path: Path to JSON file containing movie metadata.
    """

    click.echo(
        click.style(
            f"\n\n🎥 Creating vector index based on data from {input_path}...",
            bold = True,
            fg = "white"
        )
    )
    provider = RAGProvider(api_key = api_key)
    provider.create_index()

    click.echo(
        click.style(
            "\n✨ Finished!",
            bold = True,
            fg = "white"
        )
    )

def get_data(path: str, sample: float , debug: bool = False,start: int = 1960, end: int =2020):
    """
    Downloads WikiData for movies.

    Params:
        start: Starting decade.
        end: Ending decade.
        path: Path where JSON file will be saved.
    """

    if debug:
        logging.basicConfig(level="DEBUG")

    try:
        path = pathlib.Path(path)
        target_path = f"{str(path)}/movies.json"
        click.echo(
            click.style(
                "\n🍿 Downloading movie data...\n",
                bold=True,
                fg="cyan"
            )
        )

        movies_df = get_movies(start=start, end=end)
        if sample < 1.0:
            movies_df = movies_df.sample(frac=sample)
        movies_df.to_json(target_path, orient="records")

        click.echo(
            click.style(
                f"\n✨ Successfully downloaded metadata from {len(movies_df)} movies into {target_path} 😀\n",
                bold=True,
                fg="white"
            )
        )


    except Exception as exception:
        logging.error(f"Error: {str(exception)}")
        raise exception


def main():
    application = ApplicationBuilder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('query', query))
    application.run_polling()


if __name__ == "__main__":
    main()
