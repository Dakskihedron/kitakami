import discord
from discord.ext import commands

from utils.default import nsfw_blacklist
from utils.nsfw_backend import get_image

class NSFW(commands.Cog):
    """Commands related to NSFW content. Only work in channels tagged as NSFW."""
    def __init__(self, bot):
        self.bot = bot
        self.image_cache = dict()

    # Process NSFW commands and send embed or error
    async def process_nsfw(self, ctx, site: str, tags: str):
        for x in nsfw_blacklist:
            if x in tags.lower():
                return await ctx.send("One of the tags you have specified is blacklisted.")
            else:
                file_url, post_link, error = await get_image(site, tags)
                if file_url and post_link:
                    embed = discord.Embed()
                    embed.description = f'[Post Link]({post_link})'
                    embed.set_image(url=file_url)
                    msg = await ctx.send(embed=embed)
                    self.image_cache[ctx.author.id] = msg.id
                    return
                elif error:
                    return await ctx.send(error)

    @commands.command(aliases=['dan'])
    @commands.is_nsfw()
    async def danbooru(self, ctx, tags: str = ''):
        """Get a random image from Danbooru with the specified tag(s).
        Danbooru searches are limited to two tags.

        tag: str+str
        The tag(s) you want to search. Two can be searched e.g. str+str. Leave blank for random image."""
        return await self.process_nsfw(ctx, 'danbooru', tags)

    @commands.command(aliases=['gel'])
    @commands.is_nsfw()
    async def gelbooru(self, ctx, tags: str = ''):
        """Get a random image from Gelbooru with the specified tag(s).

        tag: str+str+str...
        The tag(s) you want to search. Multiple tags can be appended using plus signs e.g. str+str+str. Leave blank for random image."""
        return await self.process_nsfw(ctx, 'gelbooru', tags)

    @commands.command(aliases=['r34'])
    @commands.is_nsfw()
    async def rule34(self, ctx, tags: str = ''):
        """Get a random image from rule34.xxx with the specified tag(s).

        tag: str+str+str...
        The tag(s) you want to search. Multiple tags can be appended using plus signs e.g. str+str+str. Leave blank for random image."""
        return await self.process_nsfw(ctx, 'rule34', tags)

    @commands.command(aliases=['del', 'undo'])
    @commands.is_nsfw()
    async def deletethis(self, ctx):
        """Remove the image you recently requested."""
        try:
            msg = await ctx.channel.fetch_message(self.image_cache[ctx.author.id])
        except:
            return await ctx.send("There is no image to delete.")
        else:
            await msg.delete()
            del self.image_cache[ctx.author.id]
            return

    @danbooru.error
    @gelbooru.error
    @rule34.error
    @deletethis.error
    async def nsfw_error(self, ctx, error):
        if isinstance(error, commands.NSFWChannelRequired):
            return await ctx.send("Command can only used in a NSFW channel.")

def setup(bot):
    bot.add_cog(NSFW(bot))