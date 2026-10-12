# 💧 Hydration Reminder 3.1

### Aplicativo de lembretes de hidratação desenvolvido em Python

O **Hydration Reminder** é uma aplicação desktop para Windows desenvolvida em Python, com o objetivo de ajudar usuários a manter uma rotina de hidratação durante o trabalho, estudo ou uso do computador.

O projeto começou com notificações simples do Windows e evoluiu para uma aplicação com interface gráfica personalizada, armazenamento local e funcionamento em segundo plano.

## 🚀 Funcionalidades

- 💧 Lembretes automáticos em intervalos configuráveis.
- 🖥️ Interface gráfica desenvolvida com Tkinter.
- 🎨 Tema escuro com detalhes em azul.
- 🖼️ Suporte a imagem personalizada na interface.
- ✅ Registro de copos de água consumidos.
- 💾 Salvamento automático dos dados em JSON.
- 📅 Contador diário de hidratação.
- 🔔 Notificações personalizadas com opção de adiamento.
- 🖱️ Minimização para a bandeja do Windows.
- ⚙️ Inicialização minimizada utilizando o parâmetro `--minimized`.
- 📦 Executável Windows criado com PyInstaller.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Lógica principal da aplicação |
| Tkinter | Desenvolvimento da interface gráfica |
| Pillow | Processamento e exibição de imagens |
| Pystray | Integração com a bandeja do Windows |
| JSON | Persistência local dos dados |
| PyInstaller | Criação do executável `.exe` |

## 📸 Interface

Adicione aqui uma captura de tela da aplicação.

![Hydration Reminder](screenshots/interface.png)

## ⚙️ Como executar

**Requisitos:** Python 3 e Windows.

1. Clone este repositório.
2. Abra a pasta do projeto.
3. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

4. Execute:

```bash
python lembrete_interface_agua.py
```

Para iniciar sem mostrar a janela principal:

```bash
python lembrete_interface_agua.py --minimized
```

## 💻 Executável Windows

A aplicação também pode ser distribuída como executável utilizando PyInstaller.

```bash
python -m PyInstaller --onefile --windowed --name HydrationReminder --add-data "agua.png;." lembrete_interface_agua.py
```

O executável será criado na pasta `dist`.

Iniciar automaticamente com o Windows
1. Pressione Win + R.
2. Digite shell:startup.
3. Crie um atalho para HydrationReminder.exe nessa pasta.
4. No campo Destino das propriedades, acrescente --minimized.

## 📚 Aprendizados

Durante o desenvolvimento, pratiquei conceitos como:

- Programação orientada a objetos.
- Interfaces gráficas e manipulação de eventos.
- Agendamento de tarefas.
- Manipulação de arquivos e persistência em JSON.
- Gerenciamento de recursos e imagens.
- Integração de aplicativos com o Windows.
- Tratamento de erros, depuração e empacotamento.

## 🔮 Melhorias futuras

- Histórico semanal e mensal de hidratação.
- Metas personalizadas de consumo.
- Gráficos de acompanhamento.
- Configuração de inicialização automática pela própria interface.

## 📌 Sobre o projeto

Desenvolvido como parte dos meus estudos em **Análise e Desenvolvimento de Sistemas**, com foco na aplicação prática dos conhecimentos de Python e no desenvolvimento de soluções para problemas do cotidiano.
