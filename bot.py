import discord
from discord.ext import commands
from datetime import datetime

import emoji
import requests
from io import BytesIO
from PIL import Image

#importing token 
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track daily message counts per user
message_count = {}

@bot.event
async def on_ready():
    print(f"{bot.user} is now online and ready!")

@bot.command()
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member}'s Profile", color=discord.Color.blue())
    embed.add_field(name="Username", value=member.name, inline=False)
    embed.add_field(name="Discriminator", value=member.discriminator, inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    today = datetime.now().date()
    user_id = message.author.id

    if user_id not in message_count:
        message_count[user_id] = {}
    if today not in message_count[user_id]:
        message_count[user_id][today] = 0

    message_count[user_id][today] += 1
    await bot.process_commands(message)

@bot.command()
async def message_count_today(ctx, member: discord.Member = None):
    member = member or ctx.author
    today = datetime.now().date()
    count = message_count.get(member.id, {}).get(today, 0)
    await ctx.send(f"{member.name} has sent {count} messages today.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked for {reason}.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned for {reason}.")

# Renamed help command to octo_help
@bot.command(name="octo_help")
async def octo_help(ctx):
    embed = discord.Embed(title="Octo-Bot Commands", color=discord.Color.green())
    embed.add_field(name="!profile", value="Show profile information of a user.", inline=False)
    embed.add_field(name="!message_count_today", value="Show today's message count for a user.", inline=False)
    embed.add_field(name="!kick [user] [reason]", value="Kick a user (requires permission).", inline=False)
    embed.add_field(name="!ban [user] [reason]", value="Ban a user (requires permission).", inline=False)
    embed.add_field(name="!emoji_to_image [emoji]", value="Convert an emoji to a PNG or JPG image.", inline=False)
    embed.add_field(name="!octo_help", value="Show this help message.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def emoji_to_image(ctx, emoji_input):
    """Convert an emoji to an image format (PNG or JPG)."""
    # Check if it's a custom Discord emoji (requires specific format)
    if emoji_input.startswith("<:") and emoji_input.endswith(">"):
        # Extract custom emoji ID and fetch its URL
        emoji_id = emoji_input.split(":")[-1][:-1]
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
        response = requests.get(emoji_url)
    else:
        # Handle Unicode emoji
        emoji_code = emoji.demojize(emoji_input)
        unicode_url = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(emoji_input):x}.png"
        response = requests.get(unicode_url)

    # Check if the request was successful
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        img_format = "PNG"  # or "JPEG" if preferred
        img_path = f"emoji_image.{img_format.lower()}"
        image.save(img_path, format=img_format)

        # Send the image back to the Discord channel
        await ctx.send(file=discord.File(img_path))
    else:
        await ctx.send("Sorry, I couldn't convert that emoji to an image.")

bot.run(TOKEN)
 