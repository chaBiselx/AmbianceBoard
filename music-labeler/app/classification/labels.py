# Labels par défaut orientés JDR / soundboard
# CLAP fonctionne mieux avec des descriptions phrasées et des catégories distinctes
SOUNDBOARD_LABELS = {
    "environment": [
        "forest", "night-forest", "jungle", "swamp", "plains",
        "desert", "tundra", "mountain", "cave", "coast",
        "city", "village", "tavern", "castle", "dungeon",
        "temple", "ruins", "sewers", "harbor", "market",
        "interior", "exterior", "underground", "underwater", "aerial",
        "space", "astral-plane", "hell", "paradise", "void",
    ],
    "weather": [
        "light-rain", "heavy-rain", "storm", "thunder", "wind",
        "tempest", "blizzard", "fog", "calm-night", "dawn",
        "twilight", "heat", "cold", "silence", "day-ambience",
        "night-ambience",
    ],
    "music_style": [
        "orchestral", "epic-orchestral", "dramatic-orchestral", "soft-orchestral",
        "medieval", "celtic", "folk", "bard",
        "rock", "metal", "symphonic-metal",
        "electronic", "ambient", "dark-ambient", "synthwave",
        "jazz", "blues", "gospel",
        "tribal", "shamanic", "oriental", "asian",
        "classical", "baroque", "choir", "acapella",
        "lo-fi", "minimalist", "drone", "generic",
        "tension-build", "stinger", "sting", "jingle",
    ],
    "rolestyle": [
        "horror", "cosmic-horror", "supernatural-horror", "psychological-horror",
        "comedy", "parody", "burlesque",
        "epic", "heroic", "legendary",
        "romantic", "melancholic", "nostalgic",
        "mystery", "suspense", "thriller",
        "tragic", "dramatic", "emotional",
        "dark", "grimdark", "oppressive",
        "wonderous", "fairy-like", "dreamlike",
        "neutral", "slice-of-life", "everyday-life",
    ],
    "action": [
        "combat", "epic-combat", "loss-combat", "boss-fight", "ambush", "escape",
        "investigation", "exploration", "infiltration", "negotiation", "diplomacy",
        "journey", "crossing", "rest", "camp",
        "ritual", "magic", "summoning", "curse",
        "chase", "race", "hunt",
        "revelation", "twist", "climax", "resolution",
        "pc-death", "victory", "defeat", "betrayal",
        "puzzle", "trap", "riddle",
        "celebration", "ceremony", "festival",
    ],
    "creature": [
        "humanoid", "monster", "dragon", "undead", "demon",
        "angel", "fairy", "beast", "mechanical", "eldritch",
        "insectoid", "aquatic", "flying", "invisible", "spirit",
        "robot", "alien", "mythical", "giant", "swarm",
        "animal", "bird", "fish", "reptile", "amphibian",
    ],
    "genre": [
        "fantasy", "high-fantasy", "low-fantasy", "dark-fantasy",
        "science-fiction", "space-opera", "cyberpunk", "steampunk", "dieselpunk",
        "contemporary", "historical", "antiquity", "medieval-fantasy",
        "post-apocalyptic", "western", "piracy",
        "lovecraftian", "gothic", "victorian",
        "superhero", "urban-fantasy", "modern-horror",
        "oneshot", "campaign", "sandbox",
    ],
    "technical": [
        "loop", "one-shot", "intro", "outro", "transition",
        "background-sound", "foreground", "sfx", "music", "voice-over",
        "low-intensity", "medium-intensity", "high-intensity",
        "slow-tempo", "medium-tempo", "fast-tempo",
        "major-key", "minor-key",
        "instrumental", "with-lyrics",
        "short-duration", "long-duration",
    ],
    "sfx": [
        # Explosions / destruction
        "explosion", "shockwave",
        "blast", "detonation", "collapse", "destruction", "debris",

        # Impacts / hits
        "impact", "heavy-impact", "light-impact", "hit", "slam",
        "crash", "thud", "smash", "punch", "kick",
        "gunshot", "ricochet", "bullet-impact", "arrow-hit",
        "sword-clash", "metal-impact", "bone-crack",

        # Interference / glitches
        "interference", "radio-interference", "signal-loss", "static",
        "glitch", "distortion", "feedback", "scramble",
        "transmission", "corrupted-audio",

        # Energy / sci-fi
        "laser", "plasma-shot", "energy-burst", "electric-zap",
        "electromagnetic-pulse", "force-field", "shield-hit",
        "teleport", "warp", "scanner",

        # Horror / tension
        "scream", "whisper", "heartbeat", "breathing",
        "creak", "scratch", "growl", "monster-roar",
        "jump-scare", "tension-hit",

        # Environment interactions
        "door-open", "door-close", "door-creak",
        "footsteps", "running", "glass-break",
        "chain-rattle", "fire-crackle", "water-splash",
        "machine", "engine", "alarm", "siren",

        # UI / system sounds
        "notification", "button-click", "beep", "warning",
        "success", "failure", "countdown", "system-error",

        # Transitional / cinematic
        "whoosh", "rise", "drop", "transition-hit",
        "cinematic-boom", "reverse-hit", "stinger-sfx",
    ],
}

MACRO_TYPES = {
    "INSTANT": {
        "description": "short instantaneous sound effect or creature vocalization like explosion hit roar screech gunshot",
        "categories": ["sfx", "creature", "action"],
    },
    "AMBIANCE": {
        "description": "continuous diegetic ambient background sound like ocean waves fire crackling rain forest wind city noise",
        "categories": ["environment", "weather", "creature"],
    },
    "MUSIC": {
        "description": "extradiegetic music soundtrack or musical score like orchestral combat chase theme dramatic melody",
        "categories": ["music_style", "rolestyle", "action", "genre", "technical"],
    },
}

CATEGORY_DESCRIPTIONS = {
    "environment": "ambient background sound of a place or location like forest cave city tavern dungeon",
    "weather": "weather and natural atmosphere sounds like rain thunder wind storm blizzard",
    "music_style": "musical genre and style like orchestral medieval electronic rock jazz folk",
    "rolestyle": "emotional mood and tone like horror epic mysterious dramatic melancholic dark",
    "action": "tabletop RPG scene and action like combat exploration chase ritual celebration",
    "creature": "creature or monster sounds like dragon demon beast undead mechanical",
    "genre": "fictional universe setting like fantasy science fiction steampunk post-apocalyptic",
    "technical": "audio production type like loop intro transition background foreground intensity",
    "sfx": "short sound effect like explosion impact gunshot whoosh glitch interference alarm",
}
