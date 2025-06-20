import os
import discord
from discord.ext import commands
from gtts import gTTS
from dotenv import load_dotenv
import requests

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

def ask_openrouter(question):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": question}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error from OpenRouter: {e}"

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

@bot.command(name="ask")
async def ask(ctx, *, question):
    if not ctx.author.voice:
        await ctx.send("❌ Please join a voice channel first.")
        return

    await ctx.send("🤖 Thinking...")

    reply = ask_openrouter(question)

    if reply.startswith("❌ Error"):
        await ctx.send(reply)
        return

    try:
        tts = gTTS(reply)
        tts.save("response.mp3")
    except Exception as e:
        await ctx.send(f"🔊 TTS Error: {e}")
        return

    try:
        vc = await ctx.author.voice.channel.connect()
        vc.play(discord.FFmpegPCMAudio("response.mp3", before_options="-nostdin", options="-vn"))
        while vc.is_playing():
            await discord.utils.sleep_until(vc.is_done())
        await vc.disconnect()
    except Exception as e:
        await ctx.send(f"🎧 Voice Error: {e}")
        return

    await ctx.send(f"💬 **Answer**: {reply}")

bot.run(DISCORD_TOKEN)
