import asyncio
import discord
import random
from discord.ext import commands
from discord.ext.commands import bot
from redbot.core import commands



class MyTeam(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot 
        self.reqReadyUsers = 4 # make sure it's even
        self.team1ChannelId = 1078096640348520499 # a channelID
        self.team2ChannelId = 1078096668811083777 # a 2nd channelID
        self.setupChannelId = 1078092747937943642 # a 3rd channelID
        self.csRoleID = 1078092819316604998 # role required to use the commands this cog
        self.description=f'A bot for organizing {self.reqReadyUsers} man pugs/scrims for various {self.reqReadyUsers/2}v{self.reqReadyUsers/2} competitive games.'

        self.ourServer = None
        self.inProgress = False
        self.readyUsers = []
        self.firstCaptain = None
        self.secondCaptain = None
        self.teamOne = []
        self.teamTwo = []
        self.currentPickingCaptain = ""
        self.pickNum = 1

        
    @commands.command()
    async def readyup(self,ctx):
        """Enter the queue to find a match"""
        # we received a message

        # extract the author and message from context.
        author = ctx.author
        message = ctx.message

        # make sure they're using the bot setup channel
        if(message.channel.id != self.setupChannelId):
            # if they aren't using an appropriate channel, return1
            return 

        # ready command
        if (self.inProgress == False and len(self.readyUsers) < self.reqReadyUsers):
            # check if they are already ready
            if(author in self.readyUsers):
                embed = discord.Embed(
                    description=author.mention + "You're already ready, chill.", color=0x03f0fc)
                await ctx.send(embed=embed)
                return
            #actually readying up1
            else:
                # add them to the ready list and send a message
                self.readyUsers.append(author)
                if(len(self.readyUsers) == (self.reqReadyUsers - 2) or len(self.readyUsers) == (self.reqReadyUsers - 1)):
                    embed = discord.Embed(description="<@&" + str(self.csRoleID) + ">" + " we only need " + str(
                        self.reqReadyUsers - len(self.readyUsers)) + " more players. `[p]ready` to join", color=0x03f0fc)
                    await ctx.send(embed=embed)
                elif(len(self.readyUsers) == self.reqReadyUsers):
                    # we have 10 ready users, now need captains
                    embed = discord.Embed(
                        description="**WE BALLIN'. Now randomly selecting captains.**", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    self.inProgress = True
                    self.firstCaptain = self.readyUsers[random.randrange(len(self.readyUsers))]
                    self.readyUsers.remove(self.firstCaptain)
                    self.secondCaptain = self.readyUsers[random.randrange(len(self.readyUsers))]
                    self.readyUsers.remove(self.secondCaptain)
                    embed = discord.Embed(description="**Captains**\nTeam: " +
                                        self.firstCaptain.mention + "\nTeam: " + self.secondCaptain.mention, color=0x03f0fc)
                    await ctx.send(embed=embed)
                    embed = discord.Embed(description=self.firstCaptain.mention + " it is now your pick, pick with `" +
                                        "[p]pick @user`. Please choose from " + " \n ".join(str(x.mention) for x in self.readyUsers), color=0x03f0fc)
                    await ctx.send(embed=embed)
                elif(len(self.readyUsers) != 0):
                    embed = discord.Embed(description=author.mention + " **is now ready, we need **" + str(
                        self.reqReadyUsers - len(self.readyUsers)) + " **more**", color=0x03f0fc)
                    await ctx.send(embed=embed)
                return

    @commands.command()
    async def notready(self,ctx):
        """Exit the queue"""
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != self.setupChannelId):
            # if they aren't using an appropriate channel, return
            return 
        author = ctx.author
        try:
            self.readyUsers.remove(author)
            # unready message
            embed = discord.Embed(description=author.mention + " You are no longer ready. We now need " +
                                str(self.reqReadyUsers - len(self.readyUsers)) + " more", color=0x3f0fc)
            await ctx.send(embed=embed)
        except ValueError:
            embed = discord.Embed(description=author.mention +
                                " You are not in the ready list to begin with!", color=0x3f0fc)
            await ctx.send(embed=embed)

    @commands.command()
    async def ready(self,ctx):
        await self.readyup(ctx)
        return

    @commands.command()
    async def readyusers(self,ctx):
        await self.whosready(ctx)
        return    

    @commands.command()
    async def r(self,ctx):
        await self.readyup(ctx)
        return

    @commands.command()
    async def pick(self, ctx, *, arg):
        """As a captain, pick a player on your team"""
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != self.setupChannelId):
            # if they aren't using an appropriate channel, return
            return 
        if (self.inProgress == True and self.pickNum < (self.reqReadyUsers - 1)):
            author = ctx.author
            message = ctx.message
            guild = ctx.guild
            # make sure a captain is picking, and its his turn
            if (author == self.firstCaptain and (self.pickNum % 2 == 1)):
                # get the user they picked
                if(len(ctx.message.mentions) != 1):
                    embed = discord.Embed(
                        description="Please pick a user by @ing them. [p]pick @user", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                self.pickedUser = message.mentions[0]
                # make sure hes a real user
                if(self.pickedUser not in (name for name in self.readyUsers)):
                    embed = discord.Embed(description=str(
                        self.pickedUser) + f" `is not in the {self.reqReadyUsers} man, please pick again.`", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                # add him to team one
                self.teamOne.append(self.pickedUser)

                # move him to voice channel for team 1
                c = guild.get_channel(self.team1ChannelId)
                # await self.pickedUser.voice.channel.connect()
                await self.pickedUser.move_to(c)

                # remove him from ready users
                self.readyUsers.remove(self.pickedUser)

                # increment pick number
                self.pickNum += 1
                print(self.pickNum)


                # check if we need to pick again or its other captains turn
                if ((self.pickNum % 2) == 0):
                    embed = discord.Embed(description=self.secondCaptain.mention + " it is now your pick, pick with " +
                                       "[p]pick @user. Please choose from " + " \n ".join(str(x.mention) for x in self.readyUsers))
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=self.firstCaptain.mention + " it is now your pick, pick with " +
                                        "[p]pick @user. Please choose from " + " \n ".join(str(x.mention) for x in self.readyUsers))
                    await ctx.send(embed=embed)
                return

            elif (author == self.secondCaptain and ((self.pickNum % 2) == 0)):
                # get the user they picked
                if(len(ctx.message.mentions) != 1):
                    embed = discord.Embed(
                        description="Please pick a user by @ing them. [p]pick @user", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                self.pickedUser = ctx.message.mentions[0]
                # make sure hes a real user
                if(self.pickedUser not in (name for name in self.readyUsers)):
                    embed = discord.Embed(description=str(
                        self.pickedUser) + f" `is not in the {self.reqReadyUsers} man, please pick again.`", color=0x03f0fc)
                    await ctx.send(embed=embed)
                    return

                self.teamTwo.append(self.pickedUser)

                # move him to voice channel for team 2
                c = guild.get_channel(self.team2ChannelId)
                # await self.pickedUser.voice.channel.connect()
                await self.pickedUser.move_to(c)

                # remove him from ready users
                self.readyUsers.remove(self.pickedUser)

                self.pickNum += 1
                print(self.pickNum)

                # check if we're done picking
                if(self.pickNum == self.reqReadyUsers - 1):
                    self.teamTwo.append(self.secondCaptain)
                    self.teamOne.append(self.firstCaptain)
                    embed = discord.Embed(description='''The teams are now made and bot setup is finished.\n
                    
                    Team 1: ''' + ", ".join(str(x.name) for x in self.teamOne) +'''
                    
                    Team 2: ''' + ", ".join(str(x.name) for x in self.teamTwo) + '''
                    **Good luck and have fun!**''', color=0x3f0fc)
                    await ctx.send(embed=embed)
                    await self.firstCaptain.move_to(guild.get_channel(self.team1ChannelId))
                    await self.secondCaptain.move_to(guild.get_channel(self.team2ChannelId))
                    self.inProgress = False
                    self.readyUsers = []
                    self.teamOne = []
                    self.teamTwo = []
                    self.firstCaptain = None
                    self.secondCaptain = None
                    self.pickNum = 1
                    return

                if (self.pickNum % 2) == 1:
                    embed = discord.Embed(description=self.firstCaptain.mention + " it is now your pick, pick with [p]pick @user. Please choose from " + " \n ".join(str(x.mention) for x in self.readyUsers))
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=self.secondCaptain.mention + " it is now your pick, pick with [p]pick @user. Please choose from " + " \n ".join(str(x.mention) for x in self.readyUsers))
                    await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    description="You're not a captain, sorry, but please let the captains select!", color=0x03f0fc)
                await ctx.send(embed=embed)
        return


    @commands.command()
    async def unready(self,ctx):
        await self.notready(ctx)
        return


    @commands.command()
    async def u(self,ctx):
        await self.notready(ctx)
        return


    @commands.command()
    async def done(self,ctx):

        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != self.setupChannelId):
            # if they aren't using an appropriate channel, return
            return 
        self.inProgress = False
        self.readyUsers = []
        self.teamOne = []
        self.teamTwo = []
        self.firstCaptain = None
        self.secondCaptain = None
        self.pickNum = 1
        embed = discord.Embed(
            description=f"**Current {self.reqReadyUsers}man finished, need** {self.reqReadyUsers} **readied players**", color=0xff0000)
        await ctx.send(embed=embed)
        return


    @commands.command()
    async def whosready(self,ctx):
        """View current queued players"""
        # make sure they're using the bot setup channel
        if(ctx.message.channel.id != self.setupChannelId):
            # if they aren't using an appropriate channel, return
            await ctx.send("Wrong setup channel ID - " + str(ctx.message.channel.id))
            return 
        if (len(self.readyUsers) == 0):
            embed = discord.Embed(
                description="There is currently no players in queue!", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="__**Readied Users:**__ \n" +
                                " \n ".join(sorted(str(x.name) for x in self.readyUsers)), color=0xebe534)
            await ctx.send(embed=embed)
        return
    