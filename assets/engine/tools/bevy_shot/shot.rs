//! Harness de verificação visual do livro (não faz parte dos exemplos).
//!
//! Redireciona a câmera para uma textura, captura um quadro depois de `FRAMES` quadros
//! e fecha o app. Serve para conferir exemplos com janela em uma máquina sem sessão
//! gráfica (a superfície da janela sai preta nesses casos).
use bevy::app::AppExit;
use bevy::camera::RenderTarget;
use bevy::prelude::*;
use bevy::render::render_resource::TextureFormat;
use bevy::render::view::screenshot::{save_to_disk, Screenshot};
use bevy::ui::IsDefaultUiCamera;

pub struct Shot {
    pub path: &'static str,
    pub frames: u32,
}

#[derive(Resource)]
struct Config {
    path: &'static str,
    frames: u32,
}

#[derive(Resource)]
struct Alvo(Handle<Image>);

impl Plugin for Shot {
    fn build(&self, app: &mut App) {
        app.insert_resource(Config { path: self.path, frames: self.frames })
            .add_systems(PreStartup, criar_alvo)
            .add_systems(PostStartup, redirecionar)
            .add_systems(Last, capturar);
    }
}

fn criar_alvo(mut commands: Commands, mut imagens: ResMut<Assets<Image>>) {
    let imagem = Image::new_target_texture(800, 600, TextureFormat::Bgra8UnormSrgb, None);
    commands.insert_resource(Alvo(imagens.add(imagem)));
}

fn redirecionar(mut commands: Commands, alvo: Res<Alvo>, cameras: Query<Entity, With<Camera>>) {
    for camera in &cameras {
        commands
            .entity(camera)
            .insert((RenderTarget::Image(alvo.0.clone().into()), IsDefaultUiCamera));
    }
}

fn capturar(
    mut commands: Commands,
    alvo: Res<Alvo>,
    config: Res<Config>,
    mut quadro: Local<u32>,
    mut sair: MessageWriter<AppExit>,
) {
    *quadro += 1;
    if *quadro == config.frames {
        commands.spawn(Screenshot::image(alvo.0.clone())).observe(save_to_disk(config.path));
    }
    if *quadro == config.frames + 30 {
        sair.write(AppExit::Success);
    }
}
