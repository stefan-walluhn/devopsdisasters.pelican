Title: Config handling full circle (und immernoch daneben)
Date: 2022-03-13 16:26
Category: config handling
Tags: Config, Deployment
Quote: weil sich das so 'prima' automatisieren lässt...

Viele Teams nutzen Slack. Weniger Teams sind sich der Probleme von SaaS-Lösungen
auf US-Infrastruktur bewusst (Stichwort [Schremms
II](https://www.bfdi.bund.de/DE/Fachthemen/Inhalte/Europa-Internationales/Auswirkungen-Schrems-II-Urteil.html))
und suchen nach alternativen Lösungen. Und einige Teams landen bei einer selbst
gehosteten [Mattermost](https://mattermost.com/)-Instanz.

In Infrastructe-as-Code-Umgebungen (IaC) bedeutet selbst hosten: Das Setup wird
in Code abgebildet und anschließend durch ein Deployment ausgerollt. In einem
solchen Deployment-Code wird der Zielzustand des Setups beschrieben: Welche
Datenbanken braucht es, welche Datenbank- und Systemnutzer, welche
Webserver-Setups, welche Migrations-Schitte müssen bei einem Upgrade ausgeführt
werden, ...? Teil des Deployments ist auch die Konfiguration der Anwendung
selbst. Ziel der ganzen Übung: einen reproduzierbaren Zustand in Code
abzubilden. Hat dieser Code ein festes zu Hause im Repo einer
Versionsverwaltung, lassen sich so sowohl der Zustand eines Systems zu einem
bestimmten Zeitpunkt, als auch alle Veränderungen über die Zeit abrufen. Die
Spezifika eines Setups sind aus dem Deployment-Code sofort erkennbar, sowohl
für andere Admins, die eine solche Installation warten müssen, als auch für die
Entwickler:innen der Software, die nötige Anpassungen am Setup in
Feature-Branches des Deployment-Codes vorbereiten können. Und schließlich
ergibt sich aus IaC die Möglichkeit reproduzierbarer Setups: Eine laufende
Instanz lässt sich jederzeit auf neuer Hardware oder für weitere Installationen
ausrollen. Staging-Instanzen für die Qualitätssicherung und Abnahme neuer
Features oder Anpassungen am Setup lassen sich mit wenig Aufwand parallel
betreiben.

Die ganze Nummer geht natürlich nur auf, wenn der Zielzustand vollständig und
reproduzierbar im Deployment-Code abgebildet werden kann. Und rund um das Thema
Config-Handling hat sich ein ganzer Zoo an schlechten Ideen formiert, die dem
Ansatz von IaC entgegenstehen. Dessen Attraktionen lassen sich unter dem
Stichwort "Admin-Interfaces" zusammenfassen.

Der Schritt vom Klicki-Bunti-Desktop zu Linux-Servern ist groß und da freuen
sich viele Mitmenschen über Abkürzungen. Diese Trampelpfade münden in einem
bunten Strauß an Server-Diensten, die sich fix mit der Maus konfigurieren
lassen oder sich nach der Installation erst einmal in Form eines lustigen
Setup-Wizards präsentieren und darauf warten, zusammengeklickt zu werden. Mit
reproduzierbarer, automatisierter Konfiguration einer Anwendung hat all das
freilich wenig zu tun. Es lässt sich reichlich viel Zielzustand in Code gießen,
wenn anschließend jeder User mit Admin-Rechten wild durchs Admin-Interface
fegen kann.

Mattermost versucht einen interessanten Spagat zwischen diesen Welten und
liefert mehrere Ansätze zur Konfiguration der Anwendung: Config-Handling in der
eigenen Datenbank als klassischer Schuss ins Knie ist selbstversändlich
implementiert. Die Beschreibung von Nebenwirkungen einer solchen Verletzung
verschiebe ich auf einen späteren Zeitpunkt in einen eigenen Artikel.

Mit dem Einzug von Docker und dem damit verbundenen Config-Handling via
Environment werden in den letzten Jahren vermehrt wilde Dockerfile- und
Entrypoint-Konstruktionen direkt in sauberen Applikationscode überführt; im
Kern eine gute Entwicklung, da sich Environment-Variablen oft sehr angenehm als
IaC managen lassen.

Zum Dritten bietet Mattermost die Konfiguration per Config-File. Mit diesem
Ansatz lassen sich diverse DevOps-Disasters verwirklichen, aber gut
implementiert freut sich der:die Admin über sauber gemanagte Config-Files. Und
bis kurz vor die Zielgerade sieht das bei Mattermost vielversprechend aus:
Config im JSON-Format lässt sich mit entsprechenden JSON-Libraries problemlos
generieren und nahezu alle IaC-Lösungen und Deployment-Tools bringen
entsprechende Werkzeuge mit, um eine solche Config in wenigen Zeilen zu
generieren. Dann alles auf read-only gesetzt, damit niemend von hinten
angeschlichen kommt und heimlich an der sauber gemanagten Konfiguration
fummelt.

Setup fertig, Deployment ausgerollt, Mattermost gestartet...

    :::console
    $mattermost -c config/config.json
    Error: failed to load configuration: failed to create store: unable to load on store creation: failed to persist: failed to write file: open config/config.json: permission denied

*heul*

Mattermost startet nicht, wenn es nicht in seine eigene Config schreiben kann?
Wie zur Hölle kommt jemand auf eine solche Idee? Na klar - Irgendwie müssen die
Settings aus dem Admin-Interface persistiert werden. Und wenn Settings via
Datenbank deaktiviert sind, dann müssen die Settings aus dem UI eben direkt
zurück in das Config-File geprügelt werden... durch die Anwendung selbst.

Die ganzen nebensächlichen Implikationen (Config ist nicht im Backup; Config
wird bei Updates ggf. nicht migriert, sondern neugeschrieben; Security, jemand
zu Hause?; ...) lassen wir an dieser Stelle stillschweigend über die Bordwand
kippen.

## Lessons learned?

IaC basiert auf der Idee, einen reproduzierbaren Zustand eines Setups in Code
auszudrücken. Dieses Ziel kollidiert fundamental mit der Möglichkeit, den
Zustand eines Setups in Admin-Interfaces dynamisch klicken und ändern zu
können. Will eine Applikation beide Ansätze implementieren, muss sie
Admin-Interfaces als optionales Feature behandeln, welches deaktiviert werden
kann. Tut sie dies nicht, ist sie in professionellen Setups, die auf
IaC-Konzepten aufsetzen, nicht sicher zu betreiben. Und welche Software würde
einen solchen Anspruch für sich aufgeben?

Häufig erlebe ich allerdings, dass verschiedene Ebenen von "Setting" vermischt
und fälschlicherweise in einer einzigen Anwendungs-Domäne implementiert werden:
Die Konfiguration eines Log-Levels, von Datenbank-Anbindungen oder Mailservern
ist etwas anderes als die Aussteuerung von Berechtigungen eines Chat-Channels
durch einen Moderator oder die Frage, ob ein Account anonym angelegt werden
kann oder nicht. Die Unterteilung in Konfigurations-Domänen wie
"Integration der Anwendung im Software-Stack durch System-Admins" und
"Konfiguration von Anwendungs-Features durch Admins der Anwendung" kann helfen,
Konfigurations-Schnittstellen sauber zu trennen und für die jeweiligen
Bedürfnisse zu implementieren.

In keinem Fall aber darf der Betrieb einer Anwendung Schreibrechte auf das
eigene Config-File vorraussetzen.
