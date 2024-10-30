import discord
from discord.ext import commands
from datetime import datetime

# Import token from config
from config import TOKEN

# Define bot intents for proper permissions
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot with prefix "!" and defined intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track daily message counts per user
message_count = {}

@bot.event
async def on_ready():
    print(f"{bot.user} is now online and ready!")

@bot.command()
async def profile(ctx, member: discord.Member = None):
    """Display profile information for the specified user."""
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
    """Track the number of messages a user sends per day."""
    if message.author == bot.user:
        return
    
    today = datetime.now().date()
    user_id = message.author.id
    
    # Initialize message count if not existing
    if user_id not in message_count:
        message_count[user_id] = {}
    if today not in message_count[user_id]:
        message_count[user_id][today] = 0
    
    # Increment message count
    message_count[user_id][today] += 1
    
    await bot.process_commands(message)  # Process other commands

@bot.command()
async def message_count_today(ctx, member: discord.Member = None):
    """Display the number of messages sent today by the specified user."""
    member = member or ctx.author
    today = datetime.now().date()
    count = message_count.get(member.id, {}).get(today, 0)
    await ctx.send(f"{member.name} has sent {count} messages today.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a specified member from the server."""
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked for {reason}.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a specified member from the server."""
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned for {reason}.")

@bot.command()
async def help(ctx):
    """Display a help message with available commands."""
    embed = discord.Embed(title="Help - Bot Commands", color=discord.Color.green())
    embed.add_field(name="!profile", value="Show profile information of a user.", inline=False)
    embed.add_field(name="!message_count_today", value="Show today's message count for a user.", inline=False)
    embed.add_field(name="!kick [user] [reason]", value="Kick a user (requires permission).", inline=False)
    embed.add_field(name="!ban [user] [reason]", value="Ban a user (requires permission).", inline=False)
    embed.add_field(name="!help", value="Show this help message.", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
