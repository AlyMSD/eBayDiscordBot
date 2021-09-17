from ebaysdk.finding import Connection
import discord
from discord.ext import commands

# Your discord bot token from discord dev website
BOT_TOKEN = "PASTE YOUR BOT TOKEN HERE"

# ebay api sandbox domain (use when using sandbox API key)
sandbox_domain = 'svcs.sandbox.ebay.com'
# your ebay api sandbox key
sandbox_api_key = 'PASTE YOUR EBAY SANDBOX API KEY HERE'
# your ebay api production key
api_key = 'PASTE YOUR EBAY PRODUCTION API KEY HERE'

# variables for ebay fees
ebay_fees = [.1255, .0235]
additional_fee = .3
fee_caps = 7500

# set discord bot prefix and allow intents to get user data if needed
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


# on code run bot event
@bot.event
async def on_ready():
    # print that the bot is running to console
    print("Logged in as", bot.user.name)
    # set presence tag
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing, name="with the eBay API"))


# command to get average price of item
@bot.command()
async def avg(ctx, *, message):
    # set discord embed to send loading message before average message
    embed_loading = discord.Embed(title='LOADING', color=discord.Color.random())
    # loading gif
    embed_loading.set_thumbnail(url='https://www.inspirationde.com/media/2019/09/cd514331234507.564a1d2324e4e.gif')
    # save loading message id and send the message
    msg_load = await ctx.send(embed=embed_loading)

    # try catch for errors
    try:
        # save item entered by the user to search for
        input_query = message
        queries = message
        try:
            bought_at = message.split('[', 1)[1].split(']', 1)[0]
            queries = input_query.split('[')[0]
        except IndexError:
            bought_at = 0

        # connect to eBay API using api key and no config file | also add domain=sandbox_domain if using sandbox api key
        api = Connection(appid=api_key, config_file=None, siteid="EBAY-US")  # change site ID based on your country
        # get users query using the find Items By Keywords eBay API
        response = api.execute('findItemsByKeywords', {
            'keywords': queries
        })

        # get the queries specific item data
        items_data = response.reply.searchResult.item
        # variable to add the price of all current listings of users query
        total_price = 0
        # variable to save the number of items to later use to get the average
        num_items = 0

        # loop through all the items in the items_data dict to get the price and number of items for every item returned
        for items in items_data:
            item_price = items.sellingStatus.currentPrice.value
            total_price += float(item_price)
            num_items += 1

        # calculate average by dividing the total price by the number of items and then round to 2 decimals
        average_price = round((total_price / num_items), 2)

        total_fee = 0
        # calculates eBay fees on a marginal rate
        if average_price <= fee_caps:
            total_fee = (average_price * ebay_fees[0]) + additional_fee
        elif average_price > fee_caps:
            temp_price = average_price
            total_fee = (fee_caps * ebay_fees[0])
            temp_price -= fee_caps
            total_fee += (temp_price * ebay_fees[1]) + additional_fee

        profit = 0
        try:
            # calculate profit
            profit = round((average_price - float(bought_at)) - total_fee, 2)
        except:
            profit = round((average_price - total_fee), 2)

        # get link from api to see the listings used for average
        items_link = response.reply.itemSearchURL
        # get the first image of the eBay query to display to user
        items_img = response.reply.searchResult.item[0].galleryURL

        # set embed for the average price of the users item
        embed = discord.Embed(title='Average Price For: ' + queries, color=discord.Color.random())
        embed.add_field(name='Average Sell', value=str(average_price), inline=False)
        embed.add_field(name='Expected Profit when bought at $' + str(bought_at), value=str(profit), inline=False)
        embed.add_field(name='eBay Fee', value=str(round(total_fee, 2)), inline=False)
        embed.add_field(name='View on eBay', value='[{}]({})'.format('Click Here', items_link), inline=False)
        embed.set_thumbnail(url=items_img)
        embed.set_footer(text='Happy Selling!')
        # delete loading message
        await msg_load.delete()
        # send average embed message
        await ctx.send(embed=embed)
    # if theres an error send message in discord
    except:
        # delete loading message
        await msg_load.delete()
        await ctx.send('Looks like I can\'t find it...')

# start discord bot
bot.run(BOT_TOKEN)
