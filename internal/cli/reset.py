from internal.bootstrap.installer import run_reset


def reset():
    """Drop all core tables and reset the site."""
    run_reset()
