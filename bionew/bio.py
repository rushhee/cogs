import asyncio
import discord
token = 'YOUR TOKEN HERE'
import random
from discord.ext import commands
from discord.ext.commands import bot
from redbot.core import commands
import asyncio
import json

class MyBio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'config.json' # enter path
        self.users_file = 'users.json' # enter path

        f = open(self.config_file)
        self.data = json.load(f)

        f_users = open(self.users_file)
        self.users = json.load(f_users)


    def save(self):
        with open(self.users_file, "w") as outfile:
            json.dump(self.users, outfile)
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def askbio(self, ctx):
        """Brings up the reactable message (Admin / Bot Owner)"""
        messages = {}
        fields = self.data['biofields']
        for x in fields:
            question = fields[x]['question']
            message = await ctx.send(question)
            messages[message.id] = x
            for y in fields[x]['emojis']:
                emoji = y['emoji']
                await message.add_reaction(emoji)

        def check(reaction, user):
            return reaction.message.id in messages.keys()

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=None)
            except asyncio.TimeoutError:
                await ctx.send('Response timed out.')
            else:
                i = reaction.message.id
                field = messages[i]
                emojis = self.data['biofields'][field]['emojis']

                for e in emojis:
                    if str(reaction.emoji) == e['emoji']:
                        user_uuid = str(user.id)
                        if self.users.get(user_uuid) == None:
                            self.users[user_uuid] = {}
                            self.users[user_uuid][field] = []
                        else:
                            if self.users[user_uuid].get(field) == None:
                                self.users[user_uuid][field] = []
                                
                        
                        vals = self.users[user_uuid][field]
                        if e['name'] in vals:
                            vals.remove(e['name'])
                        else:
                            self.users[user_uuid][field].append(e['name'])
                        self.save()
                        #print(self.users)
                        await reaction.message.remove_reaction(reaction.emoji, user)
    
    @commands.command()
    async def bio(self, ctx, value: discord.Member=None):
        """Brings up your own bio or someone you tag"""
        if value is None:
            value = ctx.message.author
        user_uuid = str(value.id)
        if user_uuid in self.users:
            user_bio = self.users[user_uuid]
            embed = discord.Embed(title=f"{value.name}'s Bio", color=discord.Color.blue())
            bio_str = ""
            for bio_field, bio_info in user_bio.items():
                field_values = ", ".join(bio_info)
                bio_str = bio_str + f"\n{bio_field}: {field_values}"
            embed.add_field(name=value.name, value=f"{bio_str}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No bio found for {value.name}")



    @commands.command()
    async def searchbio(self, ctx, *values):
        """Search for values from other peoples Bios"""
        matching_users = {}
        for user_uuid, user_bio in self.users.items():
            matched_count = 0
            for bio_field, bio_info in user_bio.items():
                for value in values:
                    if value in bio_info:
                        matched_count += 1
            if matched_count == len(values):
                matching_users[user_uuid] = []

                for bio_field, bio_info in user_bio.items():
                    for value in values:
                        if value in bio_info:
                            matching_users[user_uuid].append(bio_field)

        if matching_users:
            embed = discord.Embed(title=f"Bio Search: {' '.join(values)}", color=discord.Color.blue())
            for user_uuid in matching_users:
                bio_str = ""
                user = self.bot.get_user(int(user_uuid))
                if user:
                    bio = self.users[user_uuid]
                    matched_fields = matching_users[user_uuid]
                    for field in bio:
                        if field in matched_fields:
                            field_values = ", ".join(bio[field])
                            bio_str = bio_str + f"\n{field}: {field_values}"
                embed.add_field(name=user.name, value=f"{bio_str}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No users found for {' '.join(values)}")
