#!.venv/bin/python

import datetime as dt
import enum

import requests
import typer
from decouple import config
from PIL import Image, ImageDraw, ImageFont
from typer import Option
from typing_extensions import Annotated

import inky
from inky.auto import auto

TRUETYPE_FONT = "DejaVuSans.ttf"

HA_SSL = config("HA_SSL", False, bool)
HA_HOST = config("HA_HOST", "localhost")
HA_PORT = config("HA_PORT", 8123, int)
HA_TOKEN = config("HA_TOKEN", "invalid")

HA_EID_TEMPERATURE = config("HA_ENTITY_ID_TEMPERATURE", "sensor.temperature")
HA_EID_HUMIDITY = config("HA_ENTITY_ID_HUMIDITY", "sensor.humidity")
HA_EID_WEATHER = config("HA_ENTITY_ID_WEATHER", "weather.home")

HA_SSL_METHOD = "https" if HA_SSL else "http"
HA_URL = f"{HA_SSL_METHOD}://{HA_HOST}:{HA_PORT}/api"


cli = typer.Typer()

display = auto()


class Colour(str, enum.Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    RED = "RED"

    def get_colour(self):
        if self == Colour.WHITE:
            return inky.WHITE
        if self == Colour.BLACK:
            return inky.BLACK
        if self == Colour.RED:
            return inky.RED


class HASource:

    WEATHER_ICONS = {
        "clear-night": "☾",
        "cloudy": "☁",
        "fog": "≡",
        "hail": "⁘",
        "lightning": "☇",
        "lightning-rainy": "☇",
        "partlycloudy": "☁",
        "pouring": "☵",
        "rainy": "☵",
        "snowy": "❆",
        "snowy-rainy": "❆",
        "sunny": "☀",
        "windy": "✵",
        "windy-variant": "✵",
        "exceptional": "⚠",
    }

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json",
        }

    def get_state(self, entity_id: str):
        response = requests.get(f"{self.url}/states/{entity_id}", headers=self.headers)
        if response.status_code != 200:
            print(
                f"Connection error:" f"Status code: {response.status_code}",
                f"Content: {response.text}",
                sep="\n\t",
            )
            return {}

        return response.json()

    def get_sensor(self, entity_id: str):
        data = self.get_state(entity_id)
        state: str = data.get("state", "-")
        unit = data.get("attributes", {}).get("unit_of_measurement")
        return f"{state}{unit}"

    def get_weather(self, entity_id: str):
        data = self.get_state(entity_id)
        state = data.get("state")
        return self.WEATHER_ICONS.get(state, "∅")


ha = HASource(HA_URL, HA_TOKEN)


@cli.command()
def info():
    for key in ("colour", "resolution"):
        typer.echo(f"{key.title()}: {getattr(display, key)}")
    typer.echo(f"HA url: {ha.url}")


@cli.command()
def test_ha(entity_id: str):
    typer.echo(ha.get_state(entity_id))


@cli.command()
def update(
    time_colour: Annotated[Colour, Option(case_sensitive=False)] = Colour.BLACK,
    data_colour: Annotated[Colour, Option(case_sensitive=False)] = Colour.RED,
    border: Annotated[Colour, Option(case_sensitive=False)] = Colour.BLACK,
    background: Annotated[Colour, Option(case_sensitive=False)] = Colour.WHITE,
):
    w, h = display.resolution

    image = Image.new("P", display.resolution, background.get_colour())
    canva = ImageDraw.Draw(image)

    temperature = ha.get_sensor(HA_EID_TEMPERATURE)
    humidity = ha.get_sensor(HA_EID_HUMIDITY)
    weather = ha.get_weather(HA_EID_WEATHER)

    canva.text(
        (w // 2, 16),
        dt.datetime.now().strftime("%H:%M"),
        font=ImageFont.truetype(TRUETYPE_FONT, size=60),
        anchor="mt",
        fill=time_colour.get_colour(),
    )
    canva.text(
        (w // 2, h - 10),
        f"{temperature} {weather} {humidity}",
        font=ImageFont.truetype(TRUETYPE_FONT, size=24),
        anchor="mb",
        fill=data_colour.get_colour(),
    )

    display.set_border(border.get_colour())
    display.set_image(image.rotate(180))
    display.show()


if __name__ == "__main__":
    cli()
