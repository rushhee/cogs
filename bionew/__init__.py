from .bio import MyBio


def setup(bot):
    bot.add_cog(MyBio(bot))