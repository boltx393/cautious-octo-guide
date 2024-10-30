import discord
from discord.ext import commands
from datetime import datetime

import requests
from io import BytesIO
from PIL import Image
import discord
from discord.ext import commands
import emoji

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

# help command to octo_help
@bot.command(name="octo_help")
async def octo_help(ctx):
    embed = discord.Embed(title="Octo-Bot Commands", color=discord.Color.green())
    embed.add_field(name="!profile", value="Show profile information of a user.", inline=False)
    embed.add_field(name="!message_count_today", value="Show today's message count for a user.", inline=False)
    embed.add_field(name="!kick [user] [reason]", value="Kick a user (requires permission).", inline=False)
    embed.add_field(name="!ban [user] [reason]", value="Ban a user (requires permission).", inline=False)
    embed.add_field(name="!emojiConvert [emoji]", value="Convert an emoji to a PNG or JPG image.", inline=False)
    embed.add_field(name="!octo_help", value="Show this help message.", inline=False)
    await ctx.send(embed=embed)

#emoji conversions 
@bot.command()
async def emoji_to_image(ctx, *, emoji_name: str):
    """Convert a custom emoji to an image format (PNG or JPG) or GIF for animated emojis."""
    try:
        # Check if the emoji is a custom emoji
        emoji = None
        
        # Check for custom emojis in the guild
        for guild_emoji in ctx.guild.emojis:
            if guild_emoji.name == emoji_name:
                emoji = guild_emoji
                break
        
        # If it's not a custom emoji, it could be a standard emoji
        if not emoji:
            # Try to convert the standard emoji to an image
            emoji_unicode = emoji_name.encode('utf-8').decode('unicode_escape')
            emoji = discord.Emoji(name=emoji_unicode)  # If you need to handle standard emojis

        if emoji:
            # Construct the URL for the emoji
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji.id}.png?v=1"
            gif_url = f"https://cdn.discordapp.com/emojis/{emoji.id}.gif?v=1"  # GIF URL for animated emoji
            
            response = requests.get(emoji_url)

            # If the PNG fails, try the GIF
            if response.status_code != 200:
                response = requests.get(gif_url)

            # Check if the request was successful
            if response.status_code == 200:
                img_format = "PNG" if response.headers.get('Content-Type') == 'image/png' else "GIF"
                img_path = f"emoji_image.{img_format.lower()}"
                with open(img_path, "wb") as img_file:
                    img_file.write(response.content)

                # Send the image back to the Discord channel
                await ctx.send(file=discord.File(img_path))
            else:
                await ctx.send("Sorry, I couldn't convert that emoji to an image.")
        else:
            await ctx.send("Emoji not found. Please ensure it's a valid custom emoji name.")
    except requests.exceptions.RequestException as e:
        await ctx.send("There was a network error. Please try again later.")
        print(f"Network error: {e}")
    except Exception as e:
        await ctx.send("An error occurred while processing the emoji.")
        print(f"Error: {e}")


bot.run(TOKEN)
 