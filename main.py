import discord
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import pytz

load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        channel = self.get_channel(int(os.getenv('CHANNEL_ID')))
        contests_response = requests.get('https://codeforces.com/api/contest.list?gym=false')

        try:
            contests_object = json.loads(contests_response.content)

            if(contests_object['status'] != 'OK'):
                raise Exception('Status is not OK')

            future_contest_days = int(os.getenv('FUTURE_CONTESTS_DAYS'))
            future_contests = list(filter(lambda k: k['relativeTimeSeconds'] < 0 and k['relativeTimeSeconds'] > -future_contest_days * 24 * 60 * 60, contests_object['result']))
            future_contests.reverse()

            if len(future_contests) > 0:
                description = f'Contests in the next {future_contest_days} days.'
            else:
                description = f'There are no contests in the next {future_contest_days} days.'

            embed = discord.Embed(
                title='Upcoming Codeforces contests', 
                colour=0xFF806E, 
                description=f'{description} See the whole list [here](https://codeforces.com/contests).\nCheck me out on [GitHub](https://github.com/vlahovivan/codeforces-discord-bot)!\n'
            )

            zagreb_tz = pytz.timezone("Europe/Zagreb")

            for contest in future_contests:
                contest_name = contest['name']

                is_rated = True
                max_npp = 0

                if 'Div. 2' in contest_name:
                    max_npp = 5
                elif 'Div. 3' in contest_name:
                    max_npp = 4
                else:
                    is_rated = False

                npp_string = f"This contest {f'awards at max. {max_npp}' if is_rated else 'does not award'} NatPro Points."

                date_and_time = datetime.fromtimestamp(contest['startTimeSeconds']).astimezone(zagreb_tz)

                embed.set_thumbnail(url='https://i.imgur.com/zZPUFVw.png')
                embed.add_field(name=contest_name, value=f"- {date_and_time.strftime('%B %d at %H:%M')}\n- {npp_string}", inline=False)

                embed.set_footer(text='Made by @vlahovivan.')

            await channel.send(content=f'<@&{os.getenv("TAGGED_ROLE_ID")}>', embed=embed)

        except:
            print("Something went wrong...")

        await self.close()

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.getenv('DISCORD_TOKEN'))