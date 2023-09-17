from PongGame import Game
import pygame
import neat
import os
import pickle
import visualize


class PongGame:
    FPS = 60
    FPS_MULTIPLIER = 60 / FPS  # TERRIBLE WAY TO DO THIS, if the FPS drops mid-game, the movement speed will also change
    # If you are interested in how it's properly done, search for "deltaTime in games"
    # https://en.wikipedia.org/wiki/Delta_timing
    SPEED_UP = False  # Change to True if you'd like the game to progressively speed up.
    SHOW_DECISION = True

    def __init__(self, window, width, height):
        self.game = Game(window, width, height, self.FPS_MULTIPLIER)
        self.ball = self.game.ball
        self.left_paddle = self.game.left_paddle
        self.right_paddle = self.game.right_paddle

        self.left_paddle.VEL *= self.FPS_MULTIPLIER
        self.right_paddle.VEL *= self.FPS_MULTIPLIER

    def player_vs_player(self):
        self._set_display_caption("Person vs Person")

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1
            clock.tick(self.FPS)
            self._speed_up_game()

            keys = pygame.key.get_pressed()
            self._paddle_movements(left=(keys[pygame.K_w], keys[pygame.K_s]), right=(keys[pygame.K_UP], keys[pygame.K_DOWN]))

            game_info = self.game.loop()
            self.game.draw(clock=clock, show_score=True, show_hits=False)
            pygame.display.update()

    def math_vs_math(self, corner_dist=0.3):
        """
        :param corner_dist: how close to the paddle's top/bottom corner can the ball go, recommended value: 0.05-0.48
                0.05 is very close to the corner => faster ball => a bit more intense gameplay
                0.48 is almost middle => slower ball => more relaxed game
        It would've been much better if it calculated where the ball will end up, but the collision code is too
        spaghetti to calculate the location properly, as way too many unexpected movements could happen, so for now
        the paddle simply moves down if the ball is below it, or up if the ball is above it.
        """
        self._set_display_caption("\"Math\" vs \"Math\"")

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1
            clock.tick(self.FPS)
            self._speed_up_game()

            left_up = left_down = right_up = right_down = False
            if self.ball.x < WIDTH - 350 and self.ball.x_vel < 0:
                if self.ball.y < self.left_paddle.y + corner_dist * self.left_paddle.height:
                    left_up = True
                elif self.ball.y > self.left_paddle.y + (1-corner_dist) * self.left_paddle.height:
                    left_down = True

            if self.ball.x > 350 and self.ball.x_vel > 0:
                if self.ball.y < self.right_paddle.y + corner_dist * self.right_paddle.height:
                    right_up = True
                elif self.ball.y > self.right_paddle.y + (1-corner_dist) * self.right_paddle.height:
                    right_down = True

            self._paddle_movements(left=(left_up, left_down), right=(right_up, right_down))

            game_info = self.game.loop()
            self.game.draw(clock=clock, show_score=True, show_hits=False)
            pygame.display.update()

    def player_vs_math(self, corner_dist=0.4):
        """
        :param corner_dist: how close to the paddle's top/bottom corner the ball can go, recommended value: 0.05-0.48
                0.05 is very close to the corner => faster ball => a bit more intense gameplay
                0.48 is almost middle => slower ball => more relaxed game
        """
        self._set_display_caption("Person vs \"Math\"")

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1
            clock.tick(self.FPS)
            self._speed_up_game()

            right_up = right_down = False
            # self.ball.x_vel > 0 means it moves only when the ball is going towards it, not away from it
            if self.ball.x > 350 and self.ball.x_vel > 0:
                if self.ball.y < self.right_paddle.y + corner_dist * self.right_paddle.height:
                    right_up = True
                elif self.ball.y > self.right_paddle.y + (1 - corner_dist) * self.right_paddle.height:
                    right_down = True

            keys = pygame.key.get_pressed()
            self._paddle_movements(left=(keys[pygame.K_w], keys[pygame.K_s]), right=(right_up, right_down))

            game_info = self.game.loop()
            self.game.draw(clock=clock, show_score=True, show_hits=False)
            pygame.display.update()

    def ai_vs_ai(self, genome1, genome2, config):
        self._set_display_caption("AI vs AI")

        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1
            clock.tick(self.FPS)
            self._speed_up_game()

            output1 = net1.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x + self.left_paddle.width - self.ball.x)))
            output2 = net2.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision1 = output1.index(max(output1))
            decision2 = output2.index(max(output2))

            self._paddle_movements(left=self._get_ai_move(decision1), right=self._get_ai_move(decision2))

            game_info = self.game.loop()

            self.game.draw(clock=clock, show_score=False, show_hits=True)

            if self.SHOW_DECISION:
                self._show_decision(output=output1, paddle=self.left_paddle)
                self._show_decision(output=output2, paddle=self.right_paddle)

            pygame.display.update()

    def player_vs_ai(self, genome, config):
        self._set_display_caption("Person vs AI")

        net = neat.nn.FeedForwardNetwork.create(genome, config)

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1
            clock.tick(self.FPS)
            self._speed_up_game()

            output = net.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision = output.index(max(output))

            keys = pygame.key.get_pressed()
            self._paddle_movements(left=(keys[pygame.K_w], keys[pygame.K_s]), right=(self._get_ai_move(decision)))

            game_info = self.game.loop().beans  # beans
            self.game.draw(clock=clock, show_score=True, show_hits=False)

            if self.SHOW_DECISION:
                self._show_decision(output=self._player_output(keys), paddle=self.left_paddle)
                self._show_decision(output=output, paddle=self.right_paddle)

            pygame.display.update()

    def train_ai(self, genome1, genome2, config):
        # if you are restoring from a checkpoint, then genome_generation is incorrect!
        self._set_display_caption(f"Training the AI (AI vs AI) | Generation {genome_generation}")

        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        self.game.steps = 0
        clock = pygame.time.Clock()
        while True:
            self._check_quit()
            self.game.steps += 1

            clock.tick(60)  # TODO clock.tick() for no FPS limit

            self._speed_up_game()

            output1 = net1.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x + self.left_paddle.width - self.ball.x)))
            output2 = net2.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
            decision1 = output1.index(max(output1))
            decision2 = output2.index(max(output2))

            left_decision = self._get_ai_move(decision1)
            right_decision = self._get_ai_move(decision2)
            self._paddle_movements(left=left_decision, right=right_decision)

            game_info = self.game.loop(reset_hits=False)
            self.game.draw(clock=clock, show_score=False, show_hits=True)  # TODO comment this line for epic speedup

            if self.SHOW_DECISION:
                self._show_decision(output=output1, paddle=self.left_paddle)
                self._show_decision(output=output2, paddle=self.right_paddle)

            pygame.display.update()  # TODO comment this line as well for additional speedup

            # if either side missed the ball, calculate the fitness score and end training
            if game_info.left_score > 0 or game_info.right_score > 0 or game_info.left_hits > 30 or game_info.right_hits > 30:
                self._calculate_fitness(game_info, genome1, genome2)
                break

    def _calculate_fitness(self, game_info, genome1, genome2):
        genome1.fitness += game_info.left_hits
        genome2.fitness += game_info.right_hits

    def _get_ai_move(self, decision: int):
        """
        :param decision: An int presenting AI's decision about where to move. Either 0 (stay still), 1 (up) or 2 (down).
        :return: Two bool values, indicating whether the paddle should stay still, move up or move down.
        """
        up = down = False
        if decision == 1:  # move up
            up = True
        elif decision == 2:
            down = True  # move down
        return up, down

    def _player_output(self, keys):
        """
        Translates player key presses to genome's like output, to better understand what _show_decision() shows.
        """
        player_output = [0, int(keys[pygame.K_w]), int(keys[pygame.K_s])]
        if True not in player_output:
            player_output[0] = 1
        return player_output

    def _show_decision(self, output, paddle):
        paddle_x = paddle.x + paddle.width/2
        paddle_y = paddle.y

        decision = output.index(max(output))
        safe_output = [0.001 if i == 0 else i for i in output]
        pygame.draw.circle(WIN, (255-int(200*(safe_output[1]/sum(safe_output))), 255-int(200*(safe_output[1]/sum(safe_output))), 255), (paddle_x, paddle_y+10), 5)
        pygame.draw.circle(WIN, (255-int(200*(safe_output[0]/sum(safe_output))), 255-int(200*(safe_output[0]/sum(safe_output))), 255), (paddle_x, paddle_y+50), 5)
        pygame.draw.circle(WIN, (255-int(200*(safe_output[2]/sum(safe_output))), 255-int(200*(safe_output[2]/sum(safe_output))), 255), (paddle_x, paddle_y+90), 5)

        if decision == 1:  # up
            pygame.draw.circle(WIN, (0, 0, 180), (paddle_x, paddle_y+10), 5)
        elif decision == 0:  # still
            pygame.draw.circle(WIN, (0, 0, 180), (paddle_x, paddle_y+50), 5)
        elif decision == 2:  # down
            pygame.draw.circle(WIN, (0, 0, 180), (paddle_x, paddle_y+90), 5)

    def _speed_up_game(self):
        if not self.SPEED_UP:
            return
        if self.game.steps % 60/self.FPS_MULTIPLIER == 0:
            self.ball.MAX_VEL += self.ball.MAX_VEL * 0.005
            self.left_paddle.VEL += self.left_paddle.VEL * 0.004
            self.right_paddle.VEL += self.right_paddle.VEL * 0.004

    def _paddle_movements(self, left, right):
        left_up, left_down = left
        right_up, right_down = right
        if left_up:
            self.game.move_paddle(left=True, up=True)
        elif left_down:
            self.game.move_paddle(left=True, up=False)
        if right_up:
            self.game.move_paddle(left=False, up=True)
        elif right_down:
            self.game.move_paddle(left=False, up=False)
        if True not in [left_up, left_down]:
            self.game.move_paddle(left=None, up=None, no_press_left=True, no_press_right=False)
        if True not in [right_up, right_down]:
            self.game.move_paddle(left=None, up=None, no_press_left=False, no_press_right=True)

    def _check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

    def _set_display_caption(self, text):
        pygame.display.set_caption(f"Slime Pong by @StreakyFly | {text}")


def eval_genomes(genomes, config):
    """
    Run each genome against each other once to determine the fitness.
    """
    global genome_generation

    game_num = 1
    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for (genome_id2, genome2) in genomes[i + 1:]:
            print(f"Generation: {genome_generation} | Game: {game_num}")
            game_num += 1
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness
            game = PongGame(WIN, WIDTH, HEIGHT)
            game.train_ai(genome1, genome2, config)

    genome_generation += 1


def run_neat(config, most_generations=None):
    """
    :param most_generations: at what generation should the training stop and pick a winner
    """
    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-100")  # run from a specific checkpoint/generation
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, most_generations)
    print("\n\nWinner:", winner)
    with open("best.pickle", "wb") as fb:
        pickle.dump(winner, fb)
    with open("stats.pickle", "wb") as fs:
        pickle.dump(stats, fs)


def check_stats():
    """
    Function not very useful in current state...
    """
    stats = read_pickle("stats.pickle")

    print("\n\nFitness:")
    print(stats.get_fitness_mean())
    print(stats.get_fitness_median())
    print(stats.get_fitness_stdev())

    print("\n\nGenome:")
    print(stats.best_genome())
    print(stats.best_genomes(10))
    print(stats.best_unique_genomes(10))

    print("\n\nSpecies:")
    print(stats.get_species_sizes())
    print(stats.get_species_fitness())

    visualize.plot_stats(stats, view=True)
    visualize.plot_species(stats, view=True)
    # -1, -2, -3 are input nodes, 0, 1, 2 are output nodes, other numbers are hidden layer nodes
    visualize.draw_net(config, stats.best_genome(), view=True)


def read_pickle(file):
    with open(file, "rb") as f:
        return pickle.load(f)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    WIDTH, HEIGHT = 858, 525
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Slime Pong by @StreakyFly")

    genome_generation = 1  # to keep track of which generation of genomes is currently being trained

    # run_neat(config=config, most_generations=1)  # train the AI
    # check_stats()

    game = PongGame(WIN, WIDTH, HEIGHT)

    # TODO comment/uncomment lines here, for different "modes"
    game.ai_vs_ai(read_pickle("best.pickle"), read_pickle("best2.pickle"), config)
    # game.player_vs_ai(read_pickle("best.pickle"), config)
    # game.player_vs_player()
    # game.player_vs_math(corner_dist=0.05)
    # game.math_vs_math(corner_dist=0.4)
