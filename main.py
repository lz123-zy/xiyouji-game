# 程序入口：创建 Game 对象并启动游戏主循环
from src.game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()