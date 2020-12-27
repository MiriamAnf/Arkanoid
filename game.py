import pygame
from settings import *
from sprites import *

from os import path

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("ARKANOID")
        self.clock = pygame.time.Clock()
        self.load_data()
        self.load_assets()
    
    def load_assets(self):
        self.large_font = pygame.font.SysFont('arial', 100)
        self.small_font = pygame.font.SysFont('arial', 36)

    def load_data(self):
        root_folder = path.dirname(__file__)
        fx_folder = path.join(root_folder, "sound")
        img_folder = path.join(root_folder, "img")
        self.load_fx_and_music(fx_folder)
        self.load_images(img_folder)

    def load_fx_and_music(self, fx_folder):
        self.bounce_fx = pygame.mixer.Sound(path.join(fx_folder, "bounce.wav"))
        pygame.mixer.Sound.set_volume(self.bounce_fx, 0.3)
        self.break_fx = pygame.mixer.Sound(path.join(fx_folder, "break.wav"))
        pygame.mixer.Sound.set_volume(self.break_fx, 0.3)

    def load_images(self, img_folder):
        self.pad_image = pygame.image.load(
            path.join(img_folder, "paddleRed.png"))
        self.ball_image = pygame.image.load(
            path.join(img_folder, "ballBlue.png")
        )
        brick_colors = ["blue", "purple", "green", "grey", "yellow", "red"]
        self.brick_images = []
        for color in brick_colors:
            filename = f"element_{color}_rectangle.png"
            img = pygame.image.load(path.join(img_folder, filename))
            self.brick_images.append(img)
    
    def reset(self):
        self.all_sprites = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.create_stage()
        self.player = Player(self, WIDTH//2, HEIGHT-PAD_HEIGHT*2)
        self.ball = Ball(self, WIDTH//2, HEIGHT-PAD_HEIGHT*4)
        self.score = 0
        self.life = 3

    def start(self):
        self.reset()
        self.run()

    def create_stage(self):
        for x in range(0, 11):
            for y in range(0, 7):
                Brick(
                    self,
                    BRICK_WIDTH * 2.5 + x * BRICK_WIDTH + x * 5,
                    BRICK_HEIGHT * 2.5 + y * BRICK_HEIGHT + y * 5, 
                )

    def run(self):
        self.playing = True
        while (self.playing):
            self.dt = self.clock.tick(FPS)/1000
            self.events()
            self.update()
            self.draw()
        self.game_over()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.powerup_multiball()

    def update(self):
        self.update_collisions()
        self.all_sprites.update()

    def update_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, self.balls, False)
        for ball in hits:
            ball.bounce(self.player)
            self.player.hit(ball)

        hits = pygame.sprite.groupcollide(
            self.balls, self.bricks, False, False)
        for ball, bricks in hits.items():
            the_brick = bricks[0]
            ball.bounce(the_brick)
            the_brick.hit()
            break
        if hits:
            the_brick.hit()
            self.score += 1
        if self.score == 154:
            self.victory()

    def powerup_multiball(self):
        for _ in range(10):
            reference=self.balls.sprites()[0]
            ball=Ball(self, reference.rect.centerx, reference.rect.centery)
            ball.velocity=Vector2(
                reference.velocity.x + random.uniform(-0.5, 0.5), reference.velocity.y)
            ball.isAsleep=False

    def ball_lost(self):
        self.ball=Ball(self, self.player.rect.centerx,
                         self.player.rect.top - 32)
        if self.ball_lost:
            self.life -= 1
        if self.ball_lost and self.life == 0:
            game.game_over()

    def draw(self):
        self.screen.fill(DARKGREY)
        self.all_sprites.draw(self.screen)
        self.draw_score()
        pygame.display.flip()
    
    def draw_score(self):
        score_text =self.small_font.render(
            f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))


## MAIN MENU, GAME OVER SCREEN AND VICTORY SCREEN ##
    def main_menu(self):
        title_text = self.large_font.render("ARKANOID", True, BLUE)
        instructions_text = self.small_font.render("Press any key to start!", True, LIGHTGREY)
        self.screen.fill(BGCOLOR)
        self.screen.blit(
            title_text, 
            (WIDTH//2 - title_text.get_rect().centerx, 
            HEIGHT//2 - title_text.get_rect().centery))
        self.screen.blit(
            instructions_text, 
            (WIDTH//2 - instructions_text.get_rect().centerx, 
            HEIGHT//2 - instructions_text.get_rect().centery + 64))     
        pygame.display.flip()
        pygame.time.delay(1000)

        in_main_menu = True
        while in_main_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    in_main_menu = False
        self.start()
    
    def game_over(self):
        title_text = self.large_font.render("GAME OVER", True, RED)
        instructions_text = self.small_font.render(
            f"Score: {self.score} (press any key to continue)", True, LIGHTGREY)
        self.screen.fill(BGCOLOR)
        self.screen.blit(
            title_text, 
            (WIDTH//2 - title_text.get_rect().centerx, 
            HEIGHT//2 - title_text.get_rect().centery))
        self.screen.blit(
            instructions_text, 
            (WIDTH//2 - instructions_text.get_rect().centerx, 
            HEIGHT//2 - instructions_text.get_rect().centery + 64))
        
        pygame.display.flip()
        pygame.time.delay(1000)

        in_game_over = True
        while in_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    in_game_over = False
        self.main_menu()

    def victory(self):
        title_text = self.large_font.render("YOU ARE AMAZING!", True, YELLOW)
        instructions_text = self.small_font.render(
            f"Score: {self.score} (press any key to play again)", True, LIGHTGREY)
        self.screen.fill(BGCOLOR)
        self.screen.blit(
            title_text, 
            (WIDTH//2 - title_text.get_rect().centerx, 
            HEIGHT//2 - title_text.get_rect().centery))
        self.screen.blit(
            instructions_text, 
            (WIDTH//2 - instructions_text.get_rect().centerx, 
            HEIGHT//2 - instructions_text.get_rect().centery + 64))
        
        pygame.display.flip()
        pygame.time.delay(1000)

        in_victory = True
        while in_victory:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    in_victory = False
        self.main_menu()


game = Game()
game.main_menu()