from .team import MyTeam


def setup(bot):
    bot.add_cog(MyTeam(bot))