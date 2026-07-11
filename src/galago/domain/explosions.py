class Explosion:
    def __init__(self, x, y, r, max_r, source):
        self.x = x
        self.y = y
        self.r = r
        self.max = max_r
        self.source = source  # etype ('drone'/'bee'/'boss') or 'rescue' / 'player_hit'

    def update(self):
        self.r += 2.5

    @property
    def is_done(self) -> bool:
        return self.r >= self.max
