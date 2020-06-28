import shlex
import discord
import logging
from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        role = discord.utils.get(ctx.guild.roles, name='*')
        if role is None:
            await ctx.send('No existe el rol `*`. Por favor crealo para el correcto funcionamiento del bot o contacta a un administrador.')
            return False
        user_role = ctx.author.top_role
        return user_role >= role

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Bot is ready')
        logging.info(f'Connected to {len(self.bot.guilds)} guilds:')
        for guild in self.bot.guilds:
            logging.info(f'  -> {guild.name!r} with {guild.member_count} members')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        embed = discord.Embed(
            title='Ha ocurrido un error :(',
            color=discord.Color.red()
        )
        if isinstance(error, commands.CommandNotFound):
            embed.description = f'El comando `{ctx.invoked_with}` no existe'
        elif isinstance(error, commands.CheckFailure):
            embed.description = f'No tienes permiso para ejecutar el comando `{ctx.invoked_with}`'
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f'Faltan argumentos, revisa el comando y vuelve a intentarlo'
        elif isinstance(error.original, ValueError):
            embed.description = f'Revisa los argumentos del comando, debe haber algo mal'
        elif isinstance(error.original, discord.HTTPException):
            embed.description = f'La URL especificada es inválida'
        else:
            embed.description = f'Error desconocido:\n||`{error}`||'
            await ctx.send(embed=embed)
            raise error
        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Ayuda del bot',
            description='Comandos: `++say texto` y `++embed argumento="valor"`\nTodos los argumentos para el `++embed` deben estar entre comillas dobles (`"`) o simples (`\'`).\nTodos los argumentos son opcionales pero al menos uno debe ser especificado. Para añadir un *field* se usa `"nombre del field"="valor del field"`.\nSi se necesita usar un field con el nombre de un argumento, simplemente agreguele un espacio: `"title "="valor"`.\nA continuación se listan los argumentos para el comando `++embed`:',
            color=discord.Color.blue()
        )
        embed.add_field(name='title', value='El título del embed', inline=False)
        embed.add_field(name='description', value='La descripción del embed', inline=False)
        embed.add_field(name='url', value='Convierte al título en un link, debe ser una URL válida como por ejemplo https://google.com', inline=False)
        embed.add_field(name='color', value='Color del embed, puede estar en hexadecimal (como `#FFFFFF`) o en rgb (como `255,0,0`)', inline=False)
        embed.add_field(name='author-name', value='Nombre del autor, se muestra en la parte de arriba del embed', inline=False)
        embed.add_field(name='author-icon', value='Agrega una imagen al `author`', inline=False)
        embed.add_field(name='author-url', value='Convierte al `author` en un link, parecido al argumento url', inline=False)
        embed.add_field(name='image', value='Agrega una imagen al embed, debe ser una url válida', inline=False)
        embed.add_field(name='thumbnail', value='Agrega una imágen a la derecha del embed, debe ser una url válida', inline=False)
        embed.add_field(name='footer-text', value='Agrega un texto al final del embed', inline=False)
        embed.add_field(name='footer-icon', value='Agrega una imagen al footer', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def say(self, ctx: commands.Context, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command()
    async def embed(self, ctx, *, args):
        args = dict(map(lambda arg: arg.split('='), shlex.split(args)))
        embed = discord.Embed()
        valid_attrs = ['title', 'description', 'url', 'color', 'colour', 'footer-text',
                       'footer-icon', 'author-name', 'author-icon', 'author-url', 'image', 'thumbnail']
        special_attrs = ['image', 'footer-text', 'footer-icon', 'author-name', 'author-icon', 'author-url', 'thumbnail', 'color', 'colour']
        for k, v in args.items():
            if k not in valid_attrs:
                embed.add_field(name=k, value=v, inline=False)
            else:
                if k in special_attrs:
                    if k == 'image':
                        embed.set_image(url=v)
                    elif k in special_attrs[1:3]:
                        text = args.get('footer-text', discord.Embed.Empty)
                        icon_url = args.get('footer-icon', discord.Embed.Empty)
                        embed.set_footer(text=text, icon_url=icon_url)
                    elif k in special_attrs[3:6]:
                        name = args.get('author-name', discord.Embed.Empty)
                        icon_url = args.get('author-icon', discord.Embed.Empty)
                        url = args.get('author-url', discord.Embed.Empty)
                        embed.set_author(name=name, url=url, icon_url=icon_url)
                    elif k == 'thumbnail':
                        embed.set_thumbnail(url=v)
                    elif k in special_attrs[7:9]:
                        if ',' in v:
                            colors = tuple(map(int, v.split(',')))
                            for color in colors:
                                if color >= 256:
                                    embed = discord.Embed(
                                        title='Error',
                                        description='Los colores en RGB no pueden tener valores por encima de 255, revisa el comando e intentalo de nuevo',
                                        color=discord.Color.red()
                                    )
                                    await ctx.send(embed=embed)
                                    return
                            color = discord.Color.from_rgb(*colors).value
                            setattr(embed, k, color)
                        elif '#' in v:
                            h = v.lstrip('#')
                            color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                            color = discord.Color.from_rgb(*color).value
                            setattr(embed, k, color)
                        else:
                            await ctx.send('El color especificado no es válido')
                            return
                else:
                    setattr(embed, k, v)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MainCog(bot))
