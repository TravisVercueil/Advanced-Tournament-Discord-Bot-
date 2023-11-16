import settings
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import mysql.connector
from discord import Embed
from discord.utils import get
from discord import Intents

# Database connection
mydb = mysql.connector.connect(
    host=settings.HOST,
    user=settings.USER,
    password=settings.PASSWORD,
    database=settings.USER,
)
# Global Variables
max_users = 0
type = ""
register_embed = discord.Embed
open_reg = False
checkin = False
checkin_embed = discord.Embed
finished_reg = False
second_reg = 0

def run():
    # Variable things important
    intents = discord.Intents.default()
    intents.reactions = True
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    # Prefix
    bot = commands.Bot(command_prefix="!!", intents=intents)

    # Start bot
    @bot.event
    async def on_ready():
        print("Online")

        await bot.tree.sync()

    # Error
    @bot.event
    async def on_command_error(ctx, error):
        # If error it then replies with erorr
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Error! Invalid Command!")

    # Register Command
    @bot.tree.command(name="register", description="Register for the tournament!")
    async def register(interaction: discord.Interaction):
        #Variables
        global register_embed
        global second_reg
        channel = interaction.channel
        register_channel = interaction.guild.get_channel(1136585471007412234)
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        register_channel = bot.get_channel(1136585471007412234)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        # Check if we are in the correct allocated channel
        if channel != register_channel:
            return await interaction.response.send_message(
                f"Please use the <#1136585471007412234> channel", ephemeral=True
            )
        # Check if reg is open
        if not open_reg:
            return await interaction.response.send_message(
                "Registration is Closed", ephemeral=True
            )

        # Checking if the user is already registered
        if registered_user_role in interaction.user.roles:
            await interaction.response.send_message(
                f"You are already registered {interaction.user.mention}", ephemeral=True
            )
        # Checking that the tournament is not full
        elif len(registered_user_role.members) == max_users:
            return await interaction.response.send_message(
                f"Tournament is full{interaction.user.mention}", ephemeral=True
            )
        # Registered the user if not full and giving role
        elif second_reg == 1:
            await interaction.response.send_message(
                f"You are Successfully Registered {interaction.user.mention}",
                ephemeral=True,
            )
            await interaction.user.add_roles(registered_user_role)
        elif second_reg > 1:
            await interaction.response.send_message(
                f"You are Successfully Registered {interaction.user.mention}",
                ephemeral=True,
            )
            await interaction.user.add_roles(registered_user_role)
            await interaction.user.add_roles(checkin_role)
        new_embed = discord.Embed(
            title="Registration is Open!", color=discord.Color.blue()
        )
        new_embed.add_field(
            name=f"# Of Registered Users",
            value=f"Currently {len(registered_user_role.members)} / {max_users} Registered",
            inline=True,
        )
        new_embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await register_embed.edit(embed=new_embed)

    # Unregister command
    @bot.tree.command(name="unregister", description="Unregister from the tournament")
    async def unregister(interaction: discord.Interaction):
        #Variables
        global register_embed
        channel = interaction.channel
        register_channel = interaction.guild.get_channel(1136585471007412234)
        registered_role = interaction.guild.get_role(1136917384809173042)
        #Check Correct Channel
        if channel != register_channel:
            return await interaction.response.send_message(
                f"Please use the <#1136585471007412234> channel", ephemeral=True
            )
        # Checking that there is an active tournament
        if max_users == 0:
            return await interaction.response.send_message(
                "There are currently no active tournaments", ephemeral=True
            )

        # Checking that the user has the registered role
        if registered_role in interaction.user.roles:
            await interaction.user.remove_roles(registered_role)
            await interaction.response.send_message(
                f"You are Successfully Unregistered {interaction.user.mention}",
                ephemeral=True,
            )
            register_channel = bot.get_channel(1136585471007412234)
            new_embed = discord.Embed(
                title="Registration is Open!", color=discord.Color.blue()
            )
            new_embed.add_field(
                name=f"# Of Registered Users",
                value=f"Currently {len(registered_role.members)} / {max_users} Registered",
                inline=True,
            )
            new_embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
            )
            return await register_embed.edit(embed=new_embed)
        # If no role then reply
        await interaction.response.send_message(
            f"You are not currently registered! {interaction.user.mention}",
            ephemeral=True,
        )

    # Leaderboard Command
    @bot.tree.command(name="leaderboard", description="Display the Top 10")
    async def leaderboard(interaction: discord.Interaction):
        # Variables
        global type
        x = 0
        leaderboard_points = []
        leaderboard_username = []
        channel = interaction.channel
        leaderboard_channel = interaction.guild.get_channel(1136585814957109278)

        # Check if we are in the correct allocated channel
        if channel != leaderboard_channel:
            return await interaction.response.send_message(
                f"Please use the <#1136585814957109278> channel", ephemeral=True
            )
        if type == "solo":
        # Database get our top 10 from the database
            cursor = mydb.cursor()
            cursor.execute(
                "SELECT user_id, points FROM leaderboard ORDER BY points DESC LIMIT 10"
            )
            results = cursor.fetchall()
            # checking to see if there is an active leaderboard
            if len(results) < 1:
                return await interaction.response.send_message(
                    f"No Active Leaderboard", ephemeral=True
                )
            # Creating our leaderboard
            while x != len(results):
                leaderboard_points.append(results[x][1])
                user = await interaction.guild.fetch_member(results[x][0])
                leaderboard_username.append(user.name)
                x += 1
            # Creating our embed message to send to the chat
            embed = discord.Embed(title=f"Leaderboard Top 10", color=discord.Color.blue())
            embed.add_field(
                name="User",
                value="\n".join(
                    f"**{i+1})** {user}" for i, user in enumerate(leaderboard_username)
                ),
                inline=True,
            )
            embed.add_field(
                name="> Points:",
                value="\n".join(f"> {points}" for points in leaderboard_points),
                inline=True,
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
            )
        elif type == "duo":
            
            leaderboard_duos = []
            # Database get our top 10 from the database
            cursor = mydb.cursor()
            cursor.execute(
                "SELECT user_id, points, duo FROM leaderboard ORDER BY points DESC LIMIT 10"
            )
            results = cursor.fetchall()
            # checking to see if there is an active leaderboard
            if len(results) < 1:
                return await interaction.response.send_message(
                    f"No Active Leaderboard", ephemeral=True
                )
            # Creating our leaderboard
            while x != len(results):
                leaderboard_points.append(results[x][1])
                user = await interaction.guild.fetch_member(results[x][0])
                leaderboard_username.append(user.name)
                if results[x][2] == None:
                    leaderboard_duos.append("No Teammate")
                    print(results[x][2])
                else:
                    user = await interaction.guild.fetch_member(results[x][2])
                    leaderboard_duos.append(user.name)
                x += 1

            # Creating our embed message to send to the chat
            embed = discord.Embed(title=f"Leaderboard Top 10", color=discord.Color.blue())
            embed.add_field(
                name="User",
                value="\n".join(
                    f"**{i+1})** {user} + {leaderboard_duos[i]}" for i, user in enumerate(leaderboard_username)
                ),
                inline=True,
            )
            embed.add_field(
                name="> Points:",
                value="\n".join(f"> {points}" for points in leaderboard_points),
                inline=True,
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
            )
        elif type == "trio":
            leaderboard_trio1 = []
            leaderboard_trio2 = []
            # Database get our top 10 from the database
            cursor = mydb.cursor()
            cursor.execute(
                "SELECT user_id, points, duo, trio FROM leaderboard ORDER BY points DESC LIMIT 10"
            )
            results = cursor.fetchall()
            # checking to see if there is an active leaderboard
            if len(results) < 1:
                return await interaction.response.send_message(
                    f"No Active Leaderboard", ephemeral=True
                )
            # Creating our leaderboard
            while x != len(results):
                leaderboard_points.append(results[x][1])
                user = await interaction.guild.fetch_member(results[x][0])
                leaderboard_username.append(user.name)
                if results[x][2] == None or results[x][3] == None:
                    leaderboard_trio1.append("No Teammate")
                    leaderboard_trio2.append("No Teammate")
                else:
                    user1 = await interaction.guild.fetch_member(results[x][2])
                    user2 = await interaction.guild.fetch_member(results[x][3])
                    leaderboard_trio1.append(user1.name)
                    leaderboard_trio2.append(user2.name)
                x += 1

            # Creating our embed message to send to the chat
            embed = discord.Embed(title=f"Leaderboard Top 10", color=discord.Color.blue())
            embed.add_field(
                name="User",
                value="\n".join(
                    f"**{i+1})** {user} + {leaderboard_trio1[i]} + {leaderboard_trio2[i]}" for i, user in enumerate(leaderboard_username)
                ),
                inline=True,
            )
            embed.add_field(
                name="> Points:",
                value="\n".join(f"> {points}" for points in leaderboard_points),
                inline=True,
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
            )

        # Sending embed to channel
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Calculating", ephemeral=True)

    # Create Command
    @bot.tree.command(
        name="create",
        description="Create a new tournament (WARNING THIS WILL DELETE THE CURRENT LEADERBOARD AND RESET EVERYTHING)",
    )
    # Allowing the user to create a choice between what tournament type it is
    @app_commands.choices(
        type_tournament=[
            Choice(name="Solo", value="solo"),
            Choice(name="Duo", value="duo"),
            Choice(name="Trio", value="trio"),
        ]
    )
    async def create(
        interaction: discord.Interaction, type_tournament: str, ddmm: str, time: str, reg_time:str ,thumbnail: discord.Attachment
    ):
        # Variables
        global max_users
        global type
        global open_reg
        global register_embed
        global checkin
        global second_reg
        second_reg = 0
        tournament_host = interaction.guild.get_role(1050142569146884116)
        open_reg = False
        checkin = False
        type = type_tournament
        admin_channel =  interaction.guild.get_channel(1138017603034554438)
        current_channel =  interaction.channel
        reg_channel = bot.get_channel(1136585471007412234)
        teammate_role = interaction.guild.get_role(1138036441599975425)
        registered_role = interaction.guild.get_role(1136917384809173042)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        users_with_role = registered_role.members
        checkin_channel =  interaction.guild.get_channel(1138029488756760576)
        user_submit_channel =  bot.get_channel(1137029243784679606)
        leaderboard_channel =interaction.guild.get_channel(1136585814957109278)
        teammates_channel = interaction.guild.get_channel(1138027249120067645)
        submit_channel = interaction.guild.get_channel(1136585602620456960)
        tournament_announcement_channel = interaction.guild.get_channel(1138498435507572776)
        # Check to see if the user trying to create a tournament is a tournament host
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )
        date = ddmm.split("/")
        day = int(date[0])
        month = date[1].split("pm")
        month = int(month[0])
        # Checking that the day and month are valid numbers
        if day > 31:
            return await interaction.response.send_message(
                "Invalid Date", ephemeral=True
            )
        if month > 12:
            return await interaction.response.send_message(
                "Invalid Date", ephemeral=True
            )
        
        # Check in admin channel
        if admin_channel != current_channel:
            return await interaction.response.send_message(
                "Please use the <#1138017603034554438> channel", ephemeral=True
            )
        
        await interaction.response.send_message(content=
            f"Creating {type} Tournament {interaction.user.mention}",
            ephemeral=True,)
        msg = await interaction.original_response()
        # Setting max users allowed to register for the tournament
        if type == "solo":
            max_users = 99
            print(max_users)
        elif type == "duo":
            max_users = 49
            print(max_users)
        elif type == "trio":
            max_users = 32
            print(max_users)

        # Clearing all records from the database / leaderboard
        await msg.edit(content="Clearing Leaderboard")
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM leaderboard")
        mydb.commit()

        # Removing all registered roles from the members with the registered role
        await msg.edit(content="Removing Roles")
        for member in users_with_role:
            await member.remove_roles(registered_role)
        for member in checkin_role.members:
            await member.remove_roles(checkin_role)
        
        for member in teammate_role.members:
            await member.remove_roles(teammate_role)
        await msg.edit(content="Purging Channels")
        #Purge Channels chat history
        await reg_channel.purge(limit=100)
        await checkin_channel.purge(limit=100)
        await admin_channel.purge(limit=100)
        await user_submit_channel.purge(limit=100)
        await leaderboard_channel.purge(limit=100)
        await teammates_channel.purge(limit=100)
        await submit_channel.purge(limit=100)

        embed = discord.Embed(
            title=f"{type.upper()} REGISTRATION", color=discord.Color.blue()
        )
        embed.add_field(
            name=f"Registration Details:",
            value=f"Date: {ddmm}\nTime: {reg_time}",
            inline=True,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await msg.edit(content="Sending Registration Info")
        register_embed = await reg_channel.send(embed=embed)
        
        announcement_embed = discord.Embed(title=f"{type.upper()} TOURNAMENT ANNOUNCEMENT")
        announcement_embed.add_field(name="Tournament Type:",value=f"{type.upper()}")
        announcement_embed.add_field(name="Date:",value=f"{ddmm}")
        announcement_embed.add_field(name='Time:',value=f'{time}')
        announcement_embed.add_field(name='Registration:',value=f'Time: {reg_time}\n<#1136585471007412234>')
        announcement_embed.set_thumbnail(url=thumbnail)
        await tournament_announcement_channel.send(embed=announcement_embed)
        await tournament_announcement_channel.send(content = "@everyone")
        await tournament_announcement_channel.purge(limit=1)
        await msg.edit(content="Sending Announcement")
        await msg.edit(content="Tourney Created")
    # Submit Command
    @bot.tree.command(
        name="submit",
        description="Submit your scores using /Submit Placement Elims and attach a screenshot",
    )
    async def submit(
        interaction: discord.Interaction,
        placement: int,
        eliminations: int,
        screenshot: discord.Attachment,
    ):
        global type
        global max_users
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        points_counter = 0
        channel = interaction.channel
        register_channel = interaction.guild.get_channel(1136585602620456960)
        channel = interaction.channel
        userid = interaction.user.id
        discord_user_name = interaction.user.name
        user_submit_channel = interaction.guild.get_channel(1137029243784679606)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        # Check if we are in the correct allocated channel
        if channel != register_channel:
            return await interaction.response.send_message(
                f"Please use the <#1136585602620456960> channel", ephemeral=True
            )
        # Checking to see if there is an active tournament
        if max_users == 0:
            return await interaction.response.send_message(
                "There are currently no active tournaments", ephemeral=True
            )
        if checkin_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "You are not yet checked in for this tourney please wait until after checkin to submit scores",
                ephemeral=True,
            )
        
        # Formats duo / trio (solo is same as duo just more points for kills)
        trio_format = [
            30,
            25,
            23,
            20,
            19,
            18,
            17,
            16,
            15,
            14,
            13,
            12,
            11,
            10,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
        ]
        duo_format = [
            56,
            50,
            46,
            44,
            42,
            40,
            38,
            36,
            34,
            32,
            30,
            28,
            26,
            24,
            22,
            20,
            18,
            16,
            14,
            12,
            8,
            8,
            8,
            8,
            8,
            6,
            6,
            6,
            6,
            6,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
        ]

        # Checks for if they have the role, if there is an active tournament, if they entered a valid placement and elims
        if registered_user_role not in interaction.user.roles:
            return await interaction.response.send_message(
                f"You are not registered for this tournament {interaction.user.mention}",
                ephemeral=True,
            )
        if max_users == 0:
            return await interaction.response.send_message(
                "There are currently no active tournaments", ephemeral=True
            )
        if placement < 1 or placement > max_users:
            return await interaction.response.send_message(
                "Invalid Placement", ephemeral=True
            )
        if eliminations < 0 or eliminations > max_users:
            return await interaction.response.send_message(
                "Invalid Eliminations", ephemeral=True
            )

        # Check Trio Type to get point format and assign points
        if type == "trio":
            points_counter += trio_format[placement - 1] + eliminations
        if type == "duo":
            points_counter += duo_format[placement - 1] + (eliminations * 2)
        if type == "solo":
            points_counter += duo_format[placement - 1] + (eliminations * 3)

        # Create our embed message of the user submission and submit it to the user-submissions channel
        embed = discord.Embed(title=f"User Submission", color=discord.Color.blue())
        embed.add_field(
            name=f"{interaction.user.name}",
            value=f"Placement: {placement} \n Eliminations: {eliminations}",
            inline=True,
        )
        embed.set_thumbnail(url=screenshot)
        await user_submit_channel.send(embed=embed)

        # Database and get users points
        cursor = mydb.cursor()
        cursor.execute(f"SELECT * FROM leaderboard WHERE user_id = {userid}")
        result = cursor.fetchone()
        # Check if they have points or not then update accordingly
        if result:
            cursor.execute(
                f"UPDATE leaderboard SET points = points + {points_counter} WHERE user_id = {userid}"
            )
            mydb.commit()
        else:
            sql = f"INSERT INTO leaderboard (user_id, username, points) VALUES ({userid}, '{discord_user_name}', {points_counter})"
            cursor.execute(sql)
            mydb.commit()
        await interaction.response.send_message("Submission Successful", ephemeral=True)

    # Points Command
    @bot.tree.command(
        name="points", description="See the amount of points you are currently on!"
    )
    async def points(interaction: discord.Interaction):
        # Check if registered
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        userid = interaction.user.id
        # Database check points
        cursor = mydb.cursor()
        cursor.execute(f"SELECT points FROM leaderboard WHERE user_id = {userid}")
        result = cursor.fetchone()
        # Output Points
        if result:
            await interaction.response.send_message(
                f"You have {result[0]} Points", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"You have 0 Points", ephemeral=True
            )

    # Edit command
    @bot.tree.command(name="edit", description="Edit user submission")
    async def edit(
        interaction: discord.Interaction,
        old_placement: int,
        old_eliminations: int,
        new_placement: int,
        new_eliminations: int,
        member: discord.Member,
    ):
        # Variables
        points_old = 0
        points_new = 0
        global type
        trio_format = [
            30,
            25,
            23,
            20,
            19,
            18,
            17,
            16,
            15,
            14,
            13,
            12,
            11,
            10,
            9,
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
        ]
        duo_format = [
            56,
            50,
            46,
            44,
            42,
            40,
            38,
            36,
            34,
            32,
            30,
            28,
            26,
            24,
            22,
            20,
            18,
            16,
            14,
            12,
            8,
            8,
            8,
            8,
            8,
            6,
            6,
            6,
            6,
            6,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
            2,
        ]
        tournament_host = interaction.guild.get_role(1050142569146884116)
        userid = member.id
        # Checks
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )
        # Tournament Type getting old points and new points then finding the difference
        if type == "trio":
            points_old += trio_format[old_placement - 1] + old_eliminations
            points_new += trio_format[new_placement - 1] + new_eliminations
        if type == "duo":
            points_old += duo_format[old_placement - 1] + (old_eliminations * 2)
            points_new += duo_format[new_placement - 1] + (new_eliminations * 2)
        if type == "solo":
            points_old += duo_format[old_placement - 1] + (old_eliminations * 3)
            points_new += duo_format[new_placement - 1] + (new_eliminations * 3)

        points_diff = points_old - points_new

        # Database
        cursor = mydb.cursor()
        cursor.execute(f"SELECT points FROM leaderboard WHERE user_id= {userid}")
        result = cursor.fetchone()
        # Output Points
        if result:
            cursor.execute(
                f"UPDATE leaderboard SET points = points - {points_diff} WHERE user_id = {userid}"
            )
            await interaction.response.send_message(
                f"Points updated from {points_old} to {points_new}", ephemeral=True
            )
        else:
            return await interaction.response.send_message(
                f"No User Record Found", ephemeral=True
            )

    # Check Points Command
    @bot.tree.command(
        name="checkpoints", description="See the amount of points a user has!"
    )
    async def checkpoints(interaction: discord.Interaction, member: discord.Member):
        userid = member.id
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        # Check if registered
        if registered_user_role not in interaction.user.roles:
            return await interaction.response.send_message(
                f"You are not registered for this tournament {interaction.user.mention}",
                ephemeral=True,
            )
        
        # Database check points
        cursor = mydb.cursor()
        cursor.execute(f"SELECT points FROM leaderboard WHERE user_id = {userid}")
        result = cursor.fetchone()
        # Output Points
        if result:
            await interaction.response.send_message(
                f"{member} currently has {result[0]} Points", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{member} currently has 0 Points", ephemeral=True
            )

    # Open Registeration
    @bot.tree.command(name="open_registration", description="Open the registration")
    async def open_registration(interaction: discord.Interaction):
        # Variables
        tournament_host = interaction.guild.get_role(1050142569146884116)
        global open_reg
        global register_embed
        global finished_reg
        finished_reg = False
        open_reg = True
        global second_reg
        reg_channel = interaction.guild.get_channel(1136585471007412234)
        admin_channel = interaction.guild.get_channel(1138017603034554438)
        current_channel = interaction.channel
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        # Check in admin channel
        if admin_channel != current_channel:
            return await interaction.response.send_message(
                "Please use the <#1138017603034554438> channel", ephemeral=True
            )
        # Check if active tournament
        if max_users == 0:
            return await interaction.response.send_message(
                "No Active Tournament", ephemeral=True
            )
        # Check if user has perms
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )
        # Create our registration message and open registration
        
        embed = discord.Embed(title="Registration is Open!", color=discord.Color.blue())
        embed.add_field(
            name=f"# Of Registered Users",
            value=f"Currently {len(registered_user_role.members)} / {max_users} Registered",
            inline=True,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await register_embed.edit(embed=embed)
        await interaction.response.send_message(
            "Registration is now open in <#1136585471007412234>"
        )
        await reg_channel.send(content = "@everyone")
        await reg_channel.purge(limit=1)
        second_reg += 1

    # Close Registration
    @bot.tree.command(name="close_registration", description="Close the registration")
    async def close_registration(interaction: discord.Interaction):
        # Variables
        tournament_host = interaction.guild.get_role(1050142569146884116)
        global open_reg
        global register_embed
        global finished_reg
        open_reg = False
        admin_channel = interaction.guild.get_channel(1138017603034554438)
        current_channel = interaction.channel
        reg_channel = bot.get_channel(1136585471007412234)
        # Check in admin channel
        if admin_channel != current_channel:
            return await interaction.response.send_message(
                "Please use the <#1138017603034554438> channel", ephemeral=True
            )
        # Check if active tournament
        if max_users == 0:
            return await interaction.response.send_message(
                "No Active Tournament", ephemeral=True
            )
        # Check if user has perms
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )

        embed = discord.Embed(
            title="Registration is closed!", color=discord.Color.blue()
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await register_embed.edit(embed=embed)
        await interaction.response.send_message(
            "Registration is now closed in <#1136585471007412234>"
        )
        finished_reg = True

    # Add Duo
    @bot.tree.command(name="add_duo", description="Add your duo")
    async def add_duo(interaction: discord.Interaction, duo: discord.Member):
        global type
        teammate_role = interaction.guild.get_role(1138036441599975425)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        channel = interaction.channel
        teammate_channel = interaction.guild.get_channel(1138027249120067645)
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        user_id = interaction.user.id
        discord_user_name = interaction.user.name
        # Check if we are in the correct allocated channel
        if channel != teammate_channel:
            return await interaction.response.send_message(
                f"Please use the <#1138027249120067645> channel", ephemeral=True
            )
        # Check if check in is finished
        if checkin_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "You are not yet checked in for this tourney please wait until after checkin",
                ephemeral=True,
            )
        
        if interaction.user.id == duo.id:
            return await interaction.response.send_message(
                "You cannot add yourself as a teammate", ephemeral=True
            )

        # Checking that there is an active tournament
        
        if registered_user_role not in interaction.user.roles:
            await interaction.response.send_message(
                f"You are not registered for this tournament {interaction.user.mention}",
                ephemeral=True,
            )
        if type == "solo":
            return await interaction.response.send_message(
                "This is a solo tournament how do you have a teammate?", ephemeral=True
            )
        if type == "duo":
            if teammate_role in duo.roles:
                return await interaction.response.send_message(
                    "Already has teammate role", ephemeral=True
                )
            cursor = mydb.cursor()
            cursor.execute(f"SELECT duo FROM leaderboard WHERE user_id = {user_id}")
            results = cursor.fetchall()
            print(results)
            if len(results) < 1:
                await duo.add_roles(teammate_role)
            
                cursor.execute(
                    f"INSERT INTO leaderboard (user_id, username, points, duo) VALUES ({user_id}, '{discord_user_name}', 0, {duo.id})"
                )
                mydb.commit()
                return await interaction.response.send_message(
                f"{duo} has been added as a teammate", ephemeral=True
            )
            else:
                cursor.execute(
                    f"UPDATE leaderboard SET duo = {duo.id} WHERE user_id = {user_id}"
                )
                await duo.add_roles(teammate_role)
                old_duo = await interaction.guild.fetch_member(results[0][0])
                print(old_duo)
                await old_duo.remove_roles(teammate_role)
                await interaction.response.send_message(f"{old_duo} has been removed as your teammate and {duo} has been added as your new teammate!", ephemeral=True)
                
            
        if type == "trio":
            return await interaction.response.send_message(
                f"This command is for duos not trios please use /add_trio to add your trio teammates {interaction.user.mention}",
                ephemeral=True,
            )

    # Add Trio
    @bot.tree.command(name="add_trio", description="Add your trio")
    async def add_trio(
        interaction: discord.Interaction, trio1: discord.Member, trio2: discord.Member
    ):
        #Variables
        global type
        global max_users
        discord_user_name = interaction.user.name
        teammate_role = interaction.guild.get_role(1138036441599975425)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        channel = interaction.channel
        teammate_channel = interaction.guild.get_channel(1138027249120067645)
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        user_id = interaction.user.id
        # Check if we are in the correct allocated channel
        if channel != teammate_channel:
            return await interaction.response.send_message(
                f"Please use the <#1138027249120067645> channel", ephemeral=True
            )
        if max_users == 0:
            return await interaction.response.send_message(
                "There is currently no active tournaments"
            )
        if checkin_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "You are not yet checked in for this tourney please wait until after checkin",
                ephemeral=True,
            )

        if interaction.user.id == trio1.id or interaction.user.id == trio2.id:
            return await interaction.response.send_message(
                "You cannot add yourself as a teammate"
            )

        # Checking that there is an active tournament
        if registered_user_role not in interaction.user.roles:
            await interaction.response.send_message(
                f"You are not registered for this tournament {interaction.user.mention}",
                ephemeral=True,
            )
        if type == "solo":
            return await interaction.response.send_message(
                "This is a solo tournament how do you have teammates?", ephemeral=True
            )
        if type == "duo":
            return await interaction.response.send_message(
                f"This command is for trios not duos please use /add_duo to add your duo teammate {interaction.user.mention}",
                ephemeral=True,
            )
        if type == "trio":
            if teammate_role in trio1.roles:
                return await interaction.response.send_message(
                    f"{trio1} Already has teammate role", ephemeral=True
                )
            if teammate_role in trio2.roles:
                return await interaction.response.send_message(
                    f"{trio2} Already has teammate role", ephemeral=True
                )
            cursor = mydb.cursor()
            cursor.execute(f"SELECT duo, trio FROM leaderboard WHERE user_id = {user_id}")
            results = cursor.fetchall()
            print(results)
            if len(results) == 0:
                await trio1.add_roles(teammate_role)
                await trio2.add_roles(teammate_role)
                cursor.execute(f"INSERT INTO leaderboard (user_id, username, points, duo, trio) VALUES ({user_id},'{discord_user_name}', 0, {trio1.id}, {trio2.id})" )
                mydb.commit()
                return await interaction.response.send_message(f"Teammates Added", ephemeral=True)
            
            elif results[0][0] == None and results[0][1] == None:
                await trio1.add_roles(teammate_role)
                await trio2.add_roles(teammate_role)
                cursor.execute(f"UPDATE leaderboard SET duo = {trio1.id}, trio = {trio2.id} WHERE user_id = {user_id}" )
                mydb.commit()
                return await interaction.response.send_message(f"Teammates Added", ephemeral=True)
            else:
                return await interaction.response.send_message(f"Please use /change_trio to change a trio partner",ephemeral=True)   

                    

    # Open Check in
    @bot.tree.command(name="open_checkin", description="Open Check In")
    async def open_checkin(interaction: discord.Interaction):
        global checkin
        global checkin_embed
        global finished_reg
        checkin_channel = interaction.guild.get_channel(1138029488756760576)
        admin_channel = interaction.guild.get_channel(1138017603034554438)
        tournament_host = interaction.guild.get_role(1050142569146884116)

        if not finished_reg:
            return await interaction.response.send_message(
                "Registration is not finished"
            )
        if interaction.channel != admin_channel:
            return await interaction.response.send_message(
                "Please use the <#1138017603034554438> channel", ephemeral=True
            )
        # Check to see if the user trying to create a tournament is a tournament host
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )
        checkin = True

        embed = discord.Embed(title="Check In is Open!", color=discord.Color.blue())
        embed.add_field(
            name=f"# Of Checked In Users",
            value=f"Currently 0 / {max_users} Checked In!",
            inline=True,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        checkin_embed = await checkin_channel.send(embed=embed, view=CheckInButton())

        # await checkin_embed.add_reaction("✅")
        await interaction.response.send_message(
            "Checkin is now open in <#1138029488756760576>"
        )
        await checkin_channel.send(content = "@everyone")
        await checkin_channel.purge(limit=1)

    # Close Check in
    @bot.tree.command(name="close_checkin", description="Close Check In")
    async def close_checkin(interaction: discord.Interaction):
        global checkin
        global checkin_embed
        admin_channel = interaction.guild.get_channel(1138017603034554438)
        tournament_host = interaction.guild.get_role(1050142569146884116)
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        counter = 0
        
        if interaction.channel != admin_channel:
            return await interaction.response.send_message(
                "Please use the <#1138017603034554438> channel", ephemeral=True
            )
        # Check to see if the user trying to create a tournament is a tournament host
        if tournament_host not in interaction.user.roles:
            return await interaction.response.send_message(
                f"Invalid Permissions", ephemeral=True
            )
        checkin = False
        embed = discord.Embed(title="Check In is Closed!", color=discord.Color.blue())
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await checkin_embed.edit(embed=embed)

        for member in registered_user_role.members:
            if checkin_role not in member.roles:
                await member.remove_roles(registered_user_role)
                counter += 1
        await interaction.response.send_message(
            f"Check In is now Closed! \n There was {counter} users that did not check in"
        )

    @bot.tree.command(
        name="change_captain", description="Change the captain of your team"
    )
    async def change_captain(
        interaction: discord.Interaction, new_captain: discord.Member
    ):
        teammate_role = interaction.guild.get_role(1138036441599975425)
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        global type
        user_id = interaction.user.id
        user_name = interaction.user.name
        await interaction.response.send_message(content="Attempting to change captain",ephemeral=True)
        msg = await interaction.original_response()
        if type == "solo":
            return await msg.edit(content="This is a solo tourney")
        if registered_user_role not in interaction.user.roles:
            return await msg.edit(content="You are not registered for this tourney")
        if teammate_role not in new_captain.roles:
            return await msg.edit(content=f"{new_captain} does not have teammate role")
        await interaction.user.add_roles(teammate_role)
        await interaction.user.remove_roles(registered_user_role)
        await new_captain.remove_roles(teammate_role)
        await new_captain.add_roles(registered_user_role)
        await msg.edit(content=f"Your new team captain is now {new_captain}")
        await interaction.user.remove_roles(checkin_role)
        await new_captain.add_roles(checkin_role)

        if type == "trio":
            cursor = mydb.cursor()
            cursor.execute(f"SELECT duo, trio, points FROM leaderboard WHERE user_id = {user_id}")
            result = cursor.fetchall()
            duo = await interaction.guild.fetch_member(result[0][0])
            trio = await interaction.guild.fetch_member(result[0][1])
            if duo.id == new_captain.id:
                cursor.execute(f"DELETE FROM leaderboard WHERE user_id = {user_id}")
                cursor.execute(f"INSERT INTO leaderboard (user_id, username, points, duo, trio) VALUES ({new_captain.id}, '{new_captain.name}', {result[0][2]}, {user_id}, {trio.id})")
                mydb.commit()      
            elif trio.id == new_captain.id:
                cursor.execute(f"DELETE FROM leaderboard WHERE user_id = {user_id}")
                cursor.execute(f"INSERT INTO leaderboard (user_id, username, points, duo, trio) VALUES ({new_captain.id}, '{new_captain.name}', {result[0][2]}, {duo.id}, {user_id})")
                mydb.commit()
        if type == "duo":
            cursor = mydb.cursor()
            cursor.execute(f"SELECT duo, points FROM leaderboard WHERE user_id = {user_id}")
            result = cursor.fetchall()
            duo = await interaction.guild.fetch_member(result[0][0])
            if duo.id == new_captain.id:
                cursor.execute(f"DELETE FROM leaderboard WHERE user_id = {user_id}")
                cursor.execute(f"INSERT INTO leaderboard (user_id, username, points, duo, trio) VALUES ({new_captain.id}, '{new_captain.name}', {result[0][1]}, {user_id}, NULL)")
                mydb.commit() 


    @bot.tree.command(name="change_trio", description="Change a trio partner by putting your current partner then your new parter")
    async def change_trio(interaction:discord.Interaction, current_trio:discord.Member, new_trio:discord.Member):
        registered_user_role = interaction.guild.get_role(1136917384809173042)
        checkin_role = interaction.guild.get_role(1138031162707689513)
        teammate_role = interaction.guild.get_role(1138036441599975425)
        user_id = interaction.user.id
        await interaction.response.send_message(content="Trying to Update",ephemeral=True)
        msg = await interaction.original_response()
        if registered_user_role not in interaction.user.roles:
            return await msg.edit(content="You are not registered for this tournament")
        if checkin_role not in interaction.user.roles:
            return await msg.edit(content="You are not checked in for this tournament")
        if teammate_role not in current_trio.roles:
            return await msg.edit(content=f"{current_trio} is not anyone's teammate!")
        if teammate_role in new_trio.roles:
            return await msg.edit(content=f"{new_trio} is already in a team!")
        
        cursor = mydb.cursor()
        cursor.execute(f"SELECT duo, trio FROM leaderboard WHERE user_id = {user_id}")
        result = cursor.fetchall()
        if len(result) == 0:
            return await msg.edit(content="No Teammate Found")
        else:
            duo = await interaction.guild.fetch_member(result[0][0])
            trio = await interaction.guild.fetch_member(result[0][1])
            if duo.id == current_trio.id:
                cursor.execute(f"UPDATE leaderboard SET duo = {new_trio.id} WHERE user_id = {user_id}")
                mydb.commit()
                await duo.remove_roles(teammate_role)
                await new_trio.add_roles(teammate_role)
                await msg.edit(content="Updated")
                
            elif trio.id == current_trio.id:
                cursor.execute(f"UPDATE leaderboard SET trio = {new_trio.id} WHERE user_id = {user_id}")
                mydb.commit()
                await trio.remove_roles(teammate_role)
                await new_trio.add_roles(teammate_role)
                await msg.edit(content="Updated")
                

    # Start Bot with API
    bot.run(settings.DISCORD_API_SECRET)


class CheckInButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    #    self.add_item(discord.ui.Button(label="Check In", emoji="✅"))

    @discord.ui.button(label="Check In", emoji="✅", style=discord.ButtonStyle.green)
    async def checkinBtn(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global checkin_embed
        global checkin
        checkin_role = interaction.guild.get_role(1138031162707689513)
        if not checkin:
            return await interaction.response.send_message(
                "Checkin is Closed!", ephemeral=True
            )
        if checkin_role in interaction.user.roles:
            return await interaction.response.send_message(
                "You are already checked in!", ephemeral=True
            )

        await interaction.response.send_message("Checkin Successful", ephemeral=True)
        await interaction.user.add_roles(checkin_role)

        embed = discord.Embed(title="Check In is Open!", color=discord.Color.blue())
        embed.add_field(
            name=f"# Of Checked In Users",
            value=f"Currently {len(checkin_role.members)} / {max_users} Checked In!",
            inline=True,
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1137010624572960769/1137010683775549460/CC_Tournament_Bot.png"
        )
        await checkin_embed.edit(embed=embed, view=CheckInButton())



run()


# Hours Logged
# Thursday: 2 Hours
# Friday: 6 Hours
# Monday: 4.5 Hours
# Tuesday: 2.5 hours
# Wednesday: 2 hours
# Thursday: 2 Hours
# Friday 3 hours

