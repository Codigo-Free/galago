def apply_capture_pull(player, enemies) -> bool:
    """Si el jugador está siendo secuestrado, lo arrastra hacia el enemigo que
    lo tiene en el rayo y finaliza la captura al acercarse lo suficiente.
    Devuelve True si esta llamada agota las vidas del jugador (game over)."""
    if not player.captured:
        return False
    for e in enemies:
        if e.tractor_state > 0:
            player.x += (e.x - player.x) * 0.08
            player.y += (e.y - player.y) * 0.08
            if abs(player.y - e.y) < 30:
                e.has_captured = True
                e.tractor_state = 3
                player.captured = False
                player.lives -= 1
                player.inv = 180
                player.reset_position()
            break
    return player.lives <= 0


def check_beam_entry(player, enemies) -> None:
    """Marca al jugador como capturado si entra en la zona del rayo tractor activo."""
    if not player.captured and not player.is_dual and player.inv == 0:
        for e in enemies:
            if e.alive and e.tractor_state == 2:
                if player.y > e.y + 20 and abs(player.x - e.x) < 70:
                    player.captured = True
                    break
