import discord
import typing


class Convert:
    def __init__(self, guild: discord.Guild = None, member: discord.Member = None):
        self.guild = guild
        if self.guild is None and member is not None:
            self.guild = member.guild
        self.member = member

    def convert_content(self, msg: str) -> str:
        if self.guild is not None:
            msg = msg.format(
                guild=self.guild.name,
                guild_id=self.guild.id,
                member_count=self.guild.member_count
            )
        if self.member is not None:
            msg = msg.format(
                member=str(self.member),
                member_name=self.member.name,
                member_tag=self.member.discriminator,
                member_id=self.member.id,
                mention="<@{}>".format(self.member.mention)
            )
        return msg

    def convert_embed(self, data: dict) -> typing.Optional[discord.Embed]:
        if data == {}:
            return
        embed = discord.Embed()
        if data.get("title") is not None:
            embed.title = self.convert_content(
                data.get("title", discord.Embed.Empty)
            )
        if data.get("description") is not None:
            embed.description = self.convert_content(
                data.get("description", discord.Embed.Empty)
            )
        if data.get("color") is not None:
            embed.colour = data.get("color", 0)
        if data.get("fields") is not None:
            for field in data.get("fields", []):
                embed.add_field(
                    name=self.convert_content(
                        field.get("name", "")
                    ),
                    value=self.convert_content(
                        field.get("value", "")
                    ),
                    inline=field.get("inline", "")
                )
        if data.get("thumbnail") is not None:
            if self.member is not None and data.get("thumbnail") == "<@AUTHOR_AVATAR>":
                member: discord.Member = self.member
                embed.set_thumbnail(url=member.avatar_url_as(format="png", size=1024))
            elif self.guild is not None and data.get("thumbnail") == "<@GUILD>":
                icon = self.guild.icon_url_as(format="png", size=1024)
                embed.set_thumbnail(url=str(icon))
            else:
                embed._thumbnail = {
                    'url': str(data.get("thumbnail"))
                }
        if data.get("footer") is not None:
            if isinstance(data.get("footer"), str):
                text = self.convert_content(
                    data.get("footer")
                )
                icon_url = discord.Embed.Empty
            else:
                footer = data.get("footer", {})
                text = self.convert_content(
                    footer.get("text", discord.Embed.Empty)
                )
                icon_url = footer.get("icon_url", discord.Embed.Empty)
            embed.set_footer(text=text, icon_url=icon_url)
        if data.get("author") is not None:
            if isinstance(data.get("author"), str):
                text = self.convert_content(
                    data.get("author")
                )
                url = discord.Embed.Empty
                icon_url = discord.Embed.Empty
            else:
                author = data.get("author", {})
                text = self.convert_content(
                    author.get("text", discord.Embed.Empty)
                )
                url = author.get("url", discord.Embed.Empty)
                icon_url = author.get("icon_url", discord.Embed.Empty)
            embed.set_author(name=text, icon_url=icon_url, url=url)
        return embed
