Title: You name it!
Date: 2022-10-13 20:21
Category: Config handling
Tags: Dnsmasq, Config, Naming
Quote: Das ist schon so richtig bekloppt, einen Parameter 'Interface' zu nennen mit dem Ergebnis, dass sich der Dienst trotzdem an alle Interfaces bindet

Im Netz geistert dieser [alte
Witz](https://martinfowler.com/bliki/TwoHardThings.html) herum: 

> There are only two hard things in Computer Science:
>
> 1\. Naming
>
> 2\. Cache invalidation
>
> 7\. Async callbacks
>
> 3\. Off-by-one errors

Hier und heute geht es um
[Naming](https://medium.com/@pabashani.herath/clean-code-naming-conventions-4cac223de3c6).
Falsches Naming ist fies. Nur so ungefähr richtiges Naming ist fieser. Wenn wir
uns einer Software oder einem neuen Feature nähern, müssen wir uns ein mentales
Modell der jeweiligen Funktionsweise erarbeiten. Unser initiales Modell ist sehr
wahrscheinlich falsch und der Prozess des Verstehens von Programmen und
Algorithmen besteht im Kern darin, dieses mentale Modell Stück für Stück an die
realen Bestandteile und Funktionsweisen einer Software anzupassen. Dabei
stellen wir fest, dass wir manchmal zu einfach denken, oder zu kompliziert,
oder dass eine Softwarelösung [viel zu komplex
gestrickt](https://towardsdatascience.com/re-evaluating-kafka-issues-and-alternatives-for-real-time-395573418f27)
ist, oder eben das zu lösende Problem [viel zu simpel]({tag}Ansible) angeht.
Wir merken, dass eine Software aus mehr Komponenten besteht als anfangs
gedacht, oder dass wir in unserem Modell Dinge erwartet haben, die es in der
Software in dieser Form gar nicht gibt. Benutzt eine Software verwirrende oder
inkorrekte Namen für ihre Komponenten oder Funktionen, dann greifen wir auf
falsche Vorstellungen zurück, wenn wir unser mentales Modell aufbauen.

Wenn in einem Programm von "Button" die Rede ist, denken wir an einen Knopf,
den wir mit der Maus anklicken können, und nicht an eine Ansteckplakette.
Offensichtlich ist es geschickter den Begriff "Badge" zu nutzen, um Plaketten
zu beschreiben, wenn ein Programm seine Anwender:innen nicht vollkommen
verwirren möchte.

Es erweckt nun leider den Anschein, dass es einige Programme darauf anlegen,
uns dennoch zu verwirren. [Dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)
ist ein solcher Kandidat.

Dnsmasq ist ein DNS- und DHCP-Server. Viele von euch nutzen Dnsmasq, oft ohne
es zu wissen: Dnsmasq ist darauf optimiert, seinen Dienst auf Embedded-Devices
zu verrichten und tut dies erfolgreich auf diversen Plaste-Routern, die euch
eure Provider neben den Telefonanschluss zimmern.

[DNS](https://howdns.works/de/) ist als System zur Auflösung von Domains zu
IP-Adressen komplex und die Konfiguration eines vollwertigen DNS-Servers nicht
trivial. Daher bietet es sich an, Dnsmasq als leichtgewichtige Alternative auch
auf Servern oder PCs einzusetzen, wenn nur eben fix ein schmales DNS-Setup
benötigt wird. Beispiele sind kleine LANs oder VPNs, die zur besseren Nutzung
interne Domains einsetzen wollen.

Nun kommt es - gerade auf PCs unter modernen Linux-Distributionen - vor, dass
dort bereits ein [eigener
DNS-Resolver](https://www.freedesktop.org/software/systemd/man/systemd-resolved.service.html)
läuft, um lokale DNS-Anfragen zu cachen und damit schnellere Zugriffe auf
Domains zu ermöglichen. Diese lokalen Resolver lauschen unter der lokalen IP
127.0.0.1 auf Port 53, dem Standard-Port für DNS. Soll nun zusätzlich Dnsmasq
zum Einsatz kommen und der bestehende Resolver nicht komplett ersetzt werden,
müssen wir das neue Stück Software daran hindern, auch auf dem DNS-Port der
lokalen IP lauschen zu wollen, denn da ist ja bereits besetzt.

Dnsmasq kennt die Option `--listen-address`. Wie praktisch! Das ist doch genau
das, was wir hier brauchen! Also fix eine externe IP reingeklöppelt in die
Config, Service durchgestartet...

Mööööp

    :::console
    Failed to create listening socket for port 53: Address already in use

Falsch gedacht! Dnsmasq greift dreist nach 127.0.0.1 - und
scheitert mit Bravour. Und als ob das Verhalten bis hierhin nicht bereits
obskur genug wäre, haben wir uns zusätzlich eine schöne Race-Condition ins
System gebastelt: Beim nächsten Boot werden sich beide DNS-Resolver um den
DNS-Port prügeln; wer zuerst da ist, bekommt den Port. Und wer sich jetzt
dachte, na dann macht eben Dnsmasq die Namensauflösung... wieder falsch.
Dnsmasq schnappt sich den Port, antwortet aber nicht im Geringsten auf
DNS-Anfragen.

Whaaaat?

Offensichtlich passt unser mentales Modell nicht und die Software verhält sich
nicht so, wie wir das unter den gegebenen Umständen erwarten würden. Da hilft
nur ein Blick in [die
Doku](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) zum Parameter
`--listen-address`. Die Doku meint:

> Listen on the given IP address(es). [...] Note that if no --interface option
> is given, but --listen-address is, dnsmasq will not automatically listen on
> the loopback interface. To achieve this, its IP address, 127.0.0.1, must be
> explicitly given as a --listen-address option. 

Wie bitte? Ist das nicht genau das, was wir oben konfiguriert haben? Wir hatten
doch extra NICHT 127.0.0.1 in den Parameter geschrieben? Und warum taucht hier
plötzlich der Begriff "Interfaces" auf, wenn wir über IP-Adressen reden? Also
weiter in der Doku bei `--interface`. Und da finden wir folgende drollige
Erklärung:

> Listen only on the specified interface(s). Dnsmasq automatically adds the
> loopback (local) interface to the list of interfaces to use when the
> --interface option is used. [...] On Linux, when --bind-interfaces or
> --bind-dynamic are in effect, IP alias interface labels (eg "eth1:0") are
> checked, rather than interface names. In the degenerate case when an
> interface has one address, this amounts to the same thing but when an
> interface has multiple addresses it allows control over which of those
> addresses are accepted. The same effect is achievable in default mode by
> using --listen-address. A simple wildcard, consisting of a trailing '\*', can
> be used in --interface and --except-interface options. 

Ja, ich hab doch bereits geschrieben, dass es Programme gibt, die uns verwirren
wollen! Hier geht wirklich alles drunter und drüber. Nicht nur, dass sich
Dnsmasq frech Interfaces greift, die es explizit nicht nutzen sollte, es wirft
erneut IP-Adressen und Interfaces in den Ring und bringt damit Dinge zusammen,
die [nicht zusammen
gehören](https://de.wikipedia.org/wiki/Internetprotokollfamilie#TCP/IP-Referenzmodell).

Okay, nächster Versuch: Wie wäre es, wenn wir `--except-interface` auf `lo`
setzen und Dnsmasq explizit ansagen, dass es sich das Loopback-Interface nicht
greifen soll?

    :::console
    Failed to create listening socket for port 53: Address already in use

An irgendeinem Punkt muss den Entwickler:innen von Dnsmasq auch aufgefallen
sein, dass diese Herangehensweise zu Chaos und Durcheinander führt. In der Doku
zu einem weiteren Parameter `--bind-interfaces` (wtf, wir hatten doch bereits
`--interface`?) findet sich in einem Nebensatz die Auflösung des Rätsels und
erlaubt uns endlich unser mentales Modell zu vervollständigen:

> On systems which support it, dnsmasq binds the wildcard address, even when it
> is listening on only some interfaces. It then discards requests that it
> shouldn't reply to. This has the advantage of working even when interfaces
> come and go and change address. This option forces dnsmasq to really bind
> only the interfaces it is listening on. [...]

Was uns die Doku hier ganz nebenbei verrät: Unser mentales Modell ist falsch.
Dnsmasq bindet sich in der Standard-Konfiguration immer an alle IP-Adressen.
Die Parameter `--listen-address` und `--interface` dienen nur dazu,
irgendwelche internen Filter der Software mit Informationen zu versorgen und
eingehende DNS-Anfragen auf Basis dieser Filter zu verwerfen. Habt ihr glatt
überlesen, dass in der Doku die ganze Zeit von "listen", und nicht von "bind"
geschrieben wird, was? Die ganze Welt meint dasselbe, wenn von "bind to" oder
"listen on" die Rede ist. Die ganze Welt? Nein! Eine kleine Software Namens
Dnsmasq leistet wacker Widerstand! Erst die zusätzliche(!!!) Angabe des
Parameters `--bind-interfaces` (jetzt als reines Feature-Flag ohne Wert) führt
zum erwarteten Verhalten. Dass sich Dnsmasq auch in diesem Fall an IP-Adressen
und nicht an Interfaces bindet, soll hier nur noch als Nebensächlichkeit
benannt werden.

## Lessons learned?

Die Optionen `--listen-address` und `--interface` haben uns direkt auf die
falsche Fährte gelenkt. Wir konfigurieren eine Server-Software. Aus
naheliegenden Gründen dürfen wir hier davon ausgehen, dass ein Parameter mit
dem Namen "interface" die Netzwerk-Interfaces eines Systems meint, und nicht
irgendwelche internen Filter, die ein tieferes Verständnis über die spezifische
Funktionsweise der Software voraussetzen. Gleiches gilt für einen Parameter,
der den Begriff "listen" benutzt und selbstverständlich die naheliegende
Vorstellung zulässt, dass sich hier eine Software an eine IP-Adresse bindet.

Dnsmasq will mit Interfaces und IP-Adressen zurechtkommen, die zur Laufzeit
dynamisch entstehen oder verschwinden? Nachzuvollziehen bei einer Software, die
auf Routern mit verschiedensten Netzwerk-, VPN- und Switch-Ports betrieben
wird. Aber dann nennt die Parameter doch einfach entsprechend:
`--allow-interfaces`, `--deny-interfaces`, `--allow-ip-addresses`, ... Dann
lassen sich die Anwendungsdomänen sauber trennen und es wird sofort klar, dass
hier Allow- und Deny-Listen bestückt werden. Wir als Nutzer:innen würden ein
nachvollziehbares mentales Modell entwickeln und in Verbindung mit einem
korrekt arbeitenden Parameter `--listen-address` wäre erkennbar, was hier vor
sich geht.

Falsches Naming, welches wie im Fall von Dnsmasq sogar mit bereits gesetzten
Bedeutungen kollidiert, führt zu [enormer
Verwirrung](https://www.google.com/search?q=dnsmasq+failed+to+create+listening+socket+for+port+53+Address+already+in+use)
bei den Anwender:innen. Wenn ihr Software schreibt und merkt, dass euer Naming
nicht wirklich passend ausdrückt, was ein Algorithmus treibt oder sich die
Funktionalität über die Zeit verschiebt, dann nehmt euch unbedingt die Zeit
über saubere Begriffe nachzudenken. Oft finden sich mit etwas Abstand
passendere Bezeichnungen, die zu einem besseren Verständnis der implementierten
Konzepte führen.
