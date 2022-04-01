Title: #!/bin/sh sudo
Date: 2022-04-01 21:24
Category: Monitoring
Tags: Monitoring, Nagios
Quote: sudo in 'nen Script zu schreiben muss eh dazu führen, dass man sofort mit dem nassen Handtuch verprügelt wird!
Summary: Eigentlich ist es ganz simpel: Du schreibst ein Script. Und in diesem Script willst du irgendetwas am System erledigen und benötigst besondere Zugriffsrechte. Und dafür gibt es ja `sudo`. Also schreibst du in dein Script `sudo ...`. Arg! Nein! Nicht machen!!! Ende des Artikels.

Eigentlich ist es ganz simpel: Du schreibst ein Script. Und in diesem Script
willst du irgendetwas am System erledigen und benötigst besondere
Zugriffsrechte. Und dafür gibt es ja `sudo`. Also schreibst du in dein Script
`sudo ...`.

Arg! Nein! Nicht machen!!! Ende des Artikels.

Okay, okay. Da die Konstruktion
[immer](https://github.com/sensu-plugins/sensu-plugins-varnish/blob/41a3f116b7431acd4f7481bbc3f2a8b8df3ccaf5/bin/metrics-varnish.rb#L80-L84)
[wieder](https://github.com/sensu-plugins/sensu-plugins-zfs/blob/2268b75e643069f8a78aa3b8942cb585fdc070d0/lib/sensu-plugins-zfs/zpool.rb#L19-L20)
vorkommt, scheint es angebracht, ein paar Zeilen zu dem Thema zu verlieren. Zur
Veranschaulichung des Problems werfen wir einen Blick in ein Nagios-Plugin für
[pfSense](https://www.pfsense.org/). Aufgabe des Monitoring-Plugins ist es, auf
Updates zu prüfen und zu alarmieren, wenn ein solches vorliegt. Und hier der
entsprechende Code [^nagios_plugin_pfsense_code]:

    :::php
    if (file_exists("{$g['varrun_path']}/pkg.dirty")) {
    $system_pkg_version = get_system_pkg_version(false,false);
    } else {
    shell_exec("sudo touch "."{$g['varrun_path']}/pkg.dirty");
    $system_pkg_version = get_system_pkg_version(false,false);
    shell_exec("sudo rm " . "{$g['varrun_path']}/pkg.dirty");
    }

[^nagios_plugin_pfsense_code]:<https://github.com/oneoffdallas/pfsense-nagios-checks/blob/c2d3e8d21fca705ebfa710b84e16a6e081774155/check_pf_version#L14-L20>

Jaja, Qualität und Style von Monitoring-Code hatten wir bereits im [letzten
Artikel]({filename}sensu_elasticsearch_31_days.md). Das nehmen wir diesmal als
gegeben hin und widmen uns einzig und allein dem `sudo`-Teil. Obiger Code wird
von einem Monitoring-Agenten auf dem zu überwachenden System ausgeführt. Der
Agent sollte aus Sicherheitsgründen nicht als Root-User ausgeführt werden, da
wir dem Monitoring keinen Vollzugriff auf das zu überwachende System einräumen
wollen. Lassen wir das Script ohne weitere Anpassungen laufen, bekommen wir im
besten Fall eine Fehlermeldung folgender Sorte:

    :::console
    sudo: command not found

Im schlechteren Fall:

    :::console
    Sorry, try again.
    Sorry, try again.
    sudo: 3 incorrect password attempts

Und im schlechtesten Fall:

    :::console
    [sudo] password for root:

Sudo ist eine externe Abhängigkeit des Scripts, und nur, weil jedes Ubuntu das
Sudo-Paket standardmäßig mitbringt, bedeutet das noch lange nicht, dass unter
jeder Linux- oder Unix-Umgebung `sudo` als Kommando bereitsteht. Und selbst
wenn es das tut, gewährt Sudo zusätzliche Berechtigungen für einen
unprivilegierten User und muss diesen Zugriff entsprechend absichern. Ein
Monitoring-Script läuft aber nicht aus einer interaktiven Shell heraus und kann
daher auch keine Eingaben, beispielsweise einer Passwort-Abfrage,
entgegennehmen. Um ein Script mit einer solchen Sudo-Konstruktion überhaupt in
einer nicht-interaktiven Umgebung ausführen zu können, muss in die Sudo-Config
gegriffen, die Vergabe zusätzlicher Berechtigungen durch Sudo ohne Passwort
erlaubt und damit die Sicherheit des Systems insgesamt gesenkt werden.

Aber selbst wenn wir die Konfiguration von Sudo entsprechend anpassen, welche
Sudo-Regel setzen wir? Die möglichen Optionen klingen allesamt nicht wirklich
verlockend:

* Wir könnten den Sudo-Zugriff für den Monitoring-Agenten komplett ohne
  Passwort freigeben. Dann könnten wir das ganze Teil auch direkt als Root
  laufen lassen, und das wollten wir nun gerade nicht.
* Wir könnten die durch Sudo aufgerufenen Kommandos ohne Passwort freigeben, in
  diesem Fall also `sudo touch` und `sudo rm`. Äh,
  [rm](https://linux.die.net/man/1/rm), ja, ne...
* Oder, wir geben genau die Calls frei, die in diesem Script genutzt werden,
  inklusive aller Parameter (wobei ein Parameter im Script durch die Variable
  `varrun_path` gesetzt wird, welche sich dynamisch ändern kann und die wir in
  der Sudo-Config trotzdem hart coden müssten), verletzen damit das
  [DRY-Prinzip](https://de.wikipedia.org/wiki/Don%E2%80%99t_repeat_yourself)
  und rennen dann bei etwaigen Updates des Monitoring-Scripts obskuren
  Fehlerszenarien hinterher.

Und bei all dem Durcheinander, welches eine solche Konstruktion bis hierhin
schon angerichtet hat, dieses DevOps-Desaster birgt noch einen weiteren Aspekt:
Um Sudo aus einem Script heraus überhaupt zu ermöglichen, muss das aufrufende
Script einen Shell-Call ausführen. Es muss also den eigenen Kontext verlassen
und einen weiteren Prozess starten. In diesem Beispiel, um ganz banal eine
Datei zu touchen und anschließend zu löschen; beides Operationen, die sich
deutlich besser mit den Bordmitteln von PHP und damit im Kontext des
eigentlichen Programm-Codes abbilden lassen würden.

Okay, das alles muss irgendwie anders gehen. Und für einen anderen Ansatz legen
wir Sudo erst einmal zurück in die Werkzeugkiste. Sudo ist ein Tool, um auf
interaktiven Shells zusätzliche Berechtigungen für die Ausführung von Befehlen
zu erhalten und nicht für Rechtemanagement innerhalb von Scripten gedacht.

## Lessons learned?

Unix, und Linux im Besonderen, kennt Berechtigungen und bringt diverse Konzepte
mit, um den Zugriff auf Ressourcen zu verwalten. So gibt es neben Benutzern
auch Gruppen. Für den hier aufgezeigten Fall wäre es denkbar, eine Gruppe für
das Repo-Management anzulegen, die benötigten Ressourcen für den Zugriff durch
die Gruppe freizugeben und dem Monitoring-Agenten in diese Gruppe aufzunehmen.
Für komplexere Setups bieten sich [Access Control
Lists](https://wiki.archlinux.org/title/Access_Control_Lists) an. Auch eine
Entkoppelung durch Service-Architekturen, APIs oder
[Interprozesskommunikation](https://de.wikipedia.org/wiki/Interprozesskommunikation)
ist denkbar.  In jedem Fall aber möchte ich als Admin des Systems die Wahl
haben, wie ich den Zugriff auf die benötigten Ressourcen einräume, und nicht
vor ein hart eingebautes `sudo` gestellt werden, welches mir meine eigenen
Werkzeuge aus der Hand nimmt und dafür das falsche Tool zurück reicht. Das ist
schlicht und ergreifend "not your department"!

Und überhaupt, was ist da eigentlich grundsätzlich schiefgelaufen, dass die
Abfrage der Version einer Software das zugrundeliegende Software-Repository als
dirty flaggen muss? Warum ist eine reine Abfrage eines Zustands nicht frei von
Seiteneffekten?
