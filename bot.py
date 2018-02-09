import discord
import asyncio
from arxivpy.arxiv import Arxiv
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
client = discord.Client()

try:
    with open(os.path.join(dir_path, "read_papers.json"), "rb") as f:
        papers = json.load(f)
except:
    papers = {}

try:
    with open(os.path.join(dir_path, "config.json"), "rb") as f:
        config = json.load(f)
except:
    config = {
        "search": {}
    }

async def check_arxiv():
    await client.wait_until_ready()

    channel = discord.Object(id='299546992957456386')

    while not client.is_closed:

        unprocessed = []
        all_new = []
        for category, criterias in config["search"].items():

            unprocessed.extend(Arxiv.query(
                prefix=Arxiv.Prefix.subject,
                q=category,
                sort_order=Arxiv.Sort.Order.descending,
                sort_by=Arxiv.Sort.By.submitted_date,
                start=0,
                max_results=100
            ))

            for criteria in criterias:
                unprocessed.extend(Arxiv.query(
                    prefix=Arxiv.Prefix.all,
                    q=criteria,
                    sort_order=Arxiv.Sort.Order.descending,
                    sort_by=Arxiv.Sort.By.submitted_date,
                    start=0,
                    max_results=100
                ))

        # Check if exists
        for _paper in unprocessed:
            _paper_id = _paper.get_id()
            if _paper_id not in papers:
                all_new.append(_paper)
                papers[_paper_id] = None

        with open(os.path.join(dir_path, "config.json"), "w") as f:
            json.dump(config, f)

        with open(os.path.join(dir_path, "read_papers.json"), "w") as f:
            json.dump(papers, f)

        for new_paper in all_new:
            embed = discord.Embed(
                title=new_paper.title,
                description=new_paper.summary if len(new_paper.summary) < 2040 else new_paper.summary[0:2040] + ".....",
                type="rich",
                url=new_paper.page_url,
                color=0x00ff00
            )
            embed.set_author(name=', '.join(new_paper.authors))

            await client.send_message(channel, embed=embed)

        await asyncio.sleep(60*60)





@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    client.loop.create_task(check_arxiv())



@client.event
async def on_message(message):
    if not message.content.startswith('!arxiv'):
        return
    tokenized_message = message.content.split(" ")
    if len(tokenized_message) >= 2:
        if tokenized_message[1] == 'add':
            category = tokenized_message[2]

            if category not in config["search"]:
                await client.send_message(message.channel, "Added %s to the search list." % category)
                config["search"][category] = []

            try:
                title = tokenized_message[3]
                config["search"][category].append(title)
            except:
                pass

        elif tokenized_message[1] == 'frequency':
            config["frequency"] = tokenized_message[2]

        elif tokenized_message[1] == 'list':

          pass

        else:
            await client.send_message(message.channel, "\n------ Help ------\n!arxiv add <category:required> <title:optional>\n!arxiv frequency <integer>\n!arxiv list\n--------------------")


client.run('')
