# Reserva das Brisas · Teaser

Landing page de pré-lançamento do Reserva das Brisas (Basa Inc), em Senador Canedo, GO.
Página estática: HTML, CSS e JS sem dependências.
Domínio: https://reservadasbrisas.com.br (titular: SPE Reserva das Brisas, Registro.br), hospedado na HostGator da Basa.
Prévia na Hostinger: https://reservadasbrisas.grifo.agency (deploy automático a partir da `main`, será desativada).

## Estrutura

```
index.html            página publicada (gerada, não editar direto)
src/index.src.html    fonte da página
tools/build_logo.py   gera a logo em SVG e monta o index.html
tools/wordmark.json   contornos do lettering (Montserrat) já convertidos em curvas
logo/                 logo vetorial: positiva, negativa, transparente, animada e símbolo
assets/img/           imagens do hero (WebP 1920 px e 960 px para mobile) e og.jpg
```

## Editar e gerar

1. Edite `src/index.src.html`.
2. Rode `python tools/build_logo.py` (requer `pip install fonttools` apenas para regenerar o lettering:
   `python tools/build_logo.py caminho/Montserrat[wght].ttf`).
3. O `index.html` é atualizado. Tokens como `{{logo:full:neg}}`, `{{logo:mark}}`, `{{logo:lockup:neg}}`
   e `{{basa:neg}}` viram SVG inline no build.

## Deploy na HostGator

Via cPanel > Git Version Control, clonando este repositório (branch `main`).
O `.cpanel.yml` copia `index.html`, `assets/`, `logo/` e `deploy/.htaccess` (HTTPS e sem `www`)
para `~/reservadasbrisas.com.br/` (raiz do documento do domínio no cPanel). Para publicar: `git push` na `main`, depois, no cPanel,
**Update from Remote** e **Deploy HEAD Commit**. O `index.html` já vai gerado; não há build no servidor.

## Formulário

O cadastro (nome, e-mail, WhatsApp, morar/investir) envia um POST em JSON para `FORM_ENDPOINT`,
no script ao final de `src/index.src.html`. Com o endpoint vazio, a página só mostra a confirmação.
Parâmetros `utm_*`, `gclid` e `fbclid` da URL seguem junto, e o evento `lead_reserva_das_brisas`
é enviado ao `dataLayer` quando houver Google Tag Manager.

## Pendências

- Vetor oficial da logo Basa Inc (a atual é uma aproximação).
- Endpoint do CRM para o formulário.
