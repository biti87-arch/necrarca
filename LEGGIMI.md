# Grimorio del Necrarca per Android

App del **Necrarca** (Collana v2.4): gestione delle evocazioni del *Libro dei morti* e schede ricalcolate delle *Forme non morte* dell'archetipo Carnaio, con Dominio del carnaio, famiglio ricucito dell'Imbalsamatore e Orda di feticci dell'Hunga-mate.

## Scaricare e installare l'app
1. Apri la pagina **Releases** di questo repository dal telefono.
2. Tocca il file `Necrarca-N.apk` dell'ultima versione per scaricarlo.
3. Aprilo dalle notifiche o dalla cartella Download. Android chiederà di consentire l'installazione da questa fonte: consentila solo per il browser che hai usato.
4. Le versioni successive si installano sopra la precedente e i dati salvati restano.

## Come nasce l'APK
Ogni volta che si aggiorna il ramo `main`, GitHub Actions compila l'app (file `.github/workflows/apk.yml`) e pubblica una nuova release con l'APK. Si può avviare anche a mano da **Actions → Crea APK Android → Run workflow**.

## Struttura
- `www/index.html` — l'app completa (una sola pagina, funziona senza connessione). Si genera con `python3 sorgenti/build.py`.
- `sorgenti/` — modello della pagina (`template.html`), dati estratti dai manuali (`morti.json`, `forme.json`) e script di estrazione.
- `www/vendor/` — font locali (Spectral SC, IBM Plex Sans, IBM Plex Mono).
- `android/` — progetto Android generato da Capacitor 6.
- `android/app/necrarca.keystore` — chiave di firma: serve per installare gli aggiornamenti sopra la versione precedente. Non cancellarla.

# Grimorio del Necrarca per Windows
Nella pagina **Releases** ci sono anche le versioni `win-1.0.N` con due file:
- `Necrarca-…-portatile.exe` — si avvia con un doppio clic, senza installazione.
- `Necrarca-…-installazione.exe` — installa l'app con collegamento nel menu Start.

Al primo avvio Windows può mostrare "PC protetto" (l'app non ha una firma a pagamento): scegli **Ulteriori informazioni → Esegui comunque**. La compilazione è in `.github/workflows/windows.yml` e usa Electron (cartella `desktop/`).
