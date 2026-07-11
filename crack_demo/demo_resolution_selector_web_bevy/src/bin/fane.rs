use bevy::prelude::*;
use demo_resolution_selector_web_bevy::basic_app::make_basic_app;
use demo_resolution_selector_web_bevy::main_game_plugin::MainGamePlugin;

fn main() {
    make_basic_app("Fane")
        .add_plugins(MainGamePlugin)
        .run();
}
