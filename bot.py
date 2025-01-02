import discord
from discord.ext import commands
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image
import discord
from discord.ext import commands
import emoji
from pathlib import Path
import os

#importing token 
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

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

#message_count
@bot.command()
async def message_count_today(ctx, member: discord.Member = None):
    member = member or ctx.author
    today = datetime.now().date()
    count = message_count.get(member.id, {}).get(today, 0)
    await ctx.send(f"{member.name} has sent {count} messages today.")


#kick members
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked for {reason}.")

#ban members
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
def extract_frames(image):
    """Extract all frames from an animated GIF."""
    try:
        frames = []
        for frame in range(getattr(image, "n_frames", 1)):
            image.seek(frame)
            frames.append(image.copy())
        return frames
    except Exception as e:
        print(f"Frame extraction error: {e}")
        return None

@bot.command()
async def emoji_to_image(ctx, emoji_input):
    """Convert an emoji to an image format (PNG, JPG, or GIF) supporting animated emojis."""
    try:
        # Handle custom Discord emoji
        if emoji_input.startswith("<") and emoji_input.endswith(">"):
            is_animated = emoji_input.startswith("<a:")
            emoji_id = emoji_input.split(":")[-1][:-1]
            extension = "gif" if is_animated else "png"
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}?v=1"
            response = requests.get(emoji_url)
        else:
            # Handle Unicode emoji
            if len(emoji_input) != 1:
                await ctx.send("Please provide a single emoji or a valid custom emoji.")
                return
                
            # Try both animated and static versions
            emoji_hex = f"{ord(emoji_input):x}"
            urls = [
                f"https://github.com/googlefonts/noto-emoji/raw/main/animated-emoji/u{emoji_hex}.gif",
                f"https://github.com/googlefonts/noto-emoji/raw/main/png/128/emoji_u{emoji_hex}.png"
            ]
            
            response = None
            for url in urls:
                temp_response = requests.get(url)
                if temp_response.status_code == 200:
                    response = temp_response
                    break
            
            if not response:
                await ctx.send("Sorry, I couldn't find that emoji.")
                return

        if response.status_code == 200:
            # Create temp directory if it doesn't exist
            temp_dir = Path("temp_emoji")
            temp_dir.mkdir(exist_ok=True)
            
            # Load image data
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            
            # Handle both static and animated images
            if getattr(image, "is_animated", False):
                img_path = temp_dir / "emoji.gif"
                
                # Extract and save frames
                frames = extract_frames(image)
                if frames:
                    # Get duration from original GIF or default to 100ms
                    duration = image.info.get('duration', 100)
                    
                    # Save the animated GIF
                    frames[0].save(
                        img_path,
                        save_all=True,
                        append_images=frames[1:],
                        optimize=False,
                        duration=duration,
                        loop=0
                    )
                else:
                    # If frame extraction fails, save as static image
                    image.seek(0)
                    img_path = temp_dir / "emoji.png"
                    image.save(img_path, format="PNG")
            else:
                img_path = temp_dir / "emoji.png"
                image.save(img_path, format="PNG")

            # Send the image and clean up
            await ctx.send(file=discord.File(img_path))
            try:
                os.remove(img_path)
            except Exception as e:
                print(f"Cleanup error: {e}")
            
        else:
            await ctx.send("Sorry, I couldn't convert that emoji to an image.")
            
    except requests.exceptions.RequestException as e:
        await ctx.send("There was a network error. Please try again later.")
        print(f"Network error: {e}")
    except Exception as e:
        await ctx.send("An error occurred while processing the emoji.")
        print(f"Error: {e}")
        # More detailed error logging
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")

bot.run(TOKEN)
 