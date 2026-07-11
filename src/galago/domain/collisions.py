def player_bullet_hits_enemy(bullet, enemy) -> bool:
    return (
        enemy.alive
        and abs(bullet.x - enemy.x) < enemy.size + 6
        and abs(bullet.y - enemy.y) < enemy.size + 6
    )


def enemy_bullet_hits_player(bullet, player) -> bool:
    if player.is_dual:
        return (
            (abs(bullet.x - (player.x - 16)) < 14 and abs(bullet.y - player.y) < 14)
            or (abs(bullet.x - (player.x + 16)) < 14 and abs(bullet.y - player.y) < 14)
        )
    return abs(bullet.x - player.x) < 14 and abs(bullet.y - player.y) < 14


def enemy_reached_bottom(enemy, floor_y: float) -> bool:
    return enemy.alive and not enemy.swooping and enemy.y > floor_y
