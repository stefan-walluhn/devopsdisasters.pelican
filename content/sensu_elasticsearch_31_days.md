Title: Der Monat hat 31 Tage
Date: 2022-03-20 22:04
Category: Monitoring
Tags: Monitoring
Quote: Wie Jede:r weiß, hat JEDER Monat 31 Tage
Summary: Der Code von Monitoring-Plugins spielt für gewöhnlich in einer eigenen Liga: Leider tendenziell in der Kreisliga. Das Phänomen scheint so systematisch zu sein, dass es eine eigene Kategorie an DevOps-Desastern rechtfertigen würde.

Der Code von Monitoring-Plugins spielt für gewöhnlich in einer eigenen Liga:
Leider tendenziell in der Kreisliga. Das Phänomen scheint so systematisch zu
sein, dass es eine eigene Kategorie an DevOps-Desastern rechtfertigen würde.
Und deswegen jetzt und hier die neue Kategorie
[Monitoring]({category}Monitoring).

Eine fundierte Erklärung für das Phänomen kann ich nicht liefern, daher muss
ich es bei Vermutungen belassen. Monitoring-Plugins werden in erster Linie von
Ops-Menschen entwickelt, die ihren Software-Stack monitoren müssen. Und in dem
Maße, wie die Dev-Fraktion die Aspekte von stabilen Operations nicht auf dem
Schirm hat, mangelt es in der Gegenrichtung an fundiertem Dev-Wissen rund um
[Clean Code](https://www.youtube.com/watch?v=7EmboKQH8lM) und saubere
Software-Architektur (...und wenn ich dem Feedback aus unseren Dev-Teams
Glauben schenken darf, bin ich nicht frei von diesem Phänomen *hust*). Deswegen
heißt diese Seite auch Dev**Ops**-Disasters, oder was habt ihr erwartet?

Uraufführung heute mit einem [Sensu-Plugin](https://sensu.io/) für
[Elasticsearch](https://www.elastic.co/de/elasticsearch/). Elasticsearch wird
oft in Kombination mit [Logstash](https://www.elastic.co/de/logstash/) und
[Kibana](https://www.elastic.co/de/kibana/) eingesetzt, um große Mengen
Logdaten einzusammeln und auszuwerten. Die ganze Konstruktion ist unter dem
Namen ELK-Stack bekannt. In Elasticsearch werden sogenannte Indizes angelegt,
in denen die Logdaten gespeichert werden. In der Default-Konfiguration legt
Logstash täglich einen solchen Index an.

Wenn nun das Sensu-Plugin ums Eck kommt und in die Elasticsearch-Datenbank
schaut, um die oben beschriebenen Indizes zu inspizieren, muss es herausfinden,
welche Indizes untersucht werden sollen. Will ich beispielsweise wissen, ob in
der letzten Woche sinnvolle Daten geschrieben worden sind oder es signifikante
Ausreißer gibt, die ein Fehlverhalten andeuten, müssen die letzten sieben
Indizes betrachtet werden. Will ich sicherstellen, dass alte Logdaten sauber
gelöscht werden, um z.B. den Anforderungen der DSGVO zu genügen, brauche ich
alle Indizes älter als 3 Monate. Das Sensu-Plugin muss also ausrechnen, welche
Tage gemeint sind. Und hier ist der Code, der genau das versucht [^sensu_plugins_elasticsearch_code]:

    :::ruby
    curr = end_time.to_i
    start = curr

    if config[:minutes_previous] != 0
      start -= (config[:minutes_previous] * 60)
    end
    if config[:hours_previous] != 0
      start -= (config[:hours_previous] * 60 * 60)
    end
    if config[:days_previous] != 0
      start -= (config[:days_previous] * 60 * 60 * 24)
    end
    if config[:weeks_previous] != 0
      start -= (config[:weeks_previous] * 60 * 60 * 24 * 7)
    end
    if config[:months_previous] != 0
      start -= (config[:months_previous] * 60 * 60 * 24 * 7 * 31)
    end

[^sensu_plugins_elasticsearch_code]:<https://github.com/sensu-plugins/sensu-plugins-elasticsearch/blob/eb8ffeb53c4a3c12510d7491b9972ad48b46817c/lib/sensu-plugins-elasticsearch/elasticsearch-query.rb#L30-L47>

Was die Entwickler:innen dieses Monitoring-Plugins [über Zeit
glauben](https://infiniteundo.com/post/25326999628/falsehoods-programmers-believe-about-time):

* [Jede Minute hat 60 Sekunden](https://de.wikipedia.org/wiki/Schaltsekunde).
* [Jeder Tag hat 24 Stunden](https://de.wikipedia.org/wiki/Sommerzeit).
* Jeder Monat hat 31 Tage (muss ich nicht verlinken, oder?).

Im Quelltext finden sich darüber hinaus noch weitere kühne Annahmen:

* Elasticsearch wird immer in Kombination mit Logstash benutzt.
* Logstash-Indizes werden immer täglich oder stündlich angelegt.
* Alle Elasticsearch-Server werden mit UTC betrieben.

## Lessons learned?

Der Umgang mit Datum, Uhrzeit und Zeitzonen ist kompliziert und voller
Fallstricke. Neben naheliegenden Stolpersteinen wie Zeitumstellung,
Schaltjahren und Zeitzonen gibt es weniger offensichtliche Schmankerl à la Zeit
vor dem
[01.01.1970](https://www.wired.com/2001/09/unix-tick-tocks-to-a-billion/) oder
die Zeitzone
[LMT](https://stackoverflow.com/questions/35462876/python-pytz-timezone-function-returns-a-timezone-that-is-off-by-9-minutes).
[Warsaw mean time](https://en.wikipedia.org/wiki/Time_in_Poland#History)
anyone? Der Versuch, diesem Durcheinander mit selbstgestricktem Code
beizukommen, ist zum Scheitern verurteilt. Glücklicherweise unterstützen alle
modernen Betriebssysteme den Umgang mit Zeit und gängige Programmiersprachen
bringen etablierte Bibliotheken mit, die darauf aufsetzen (bspw.
[Python](https://pythonhosted.org/pytz/),
[Ruby/Rails](https://api.rubyonrails.org/classes/ActiveSupport/TimeZone.html),
[PHP](https://www.php.net/manual/de/timezones.php)). Ihr habt in eurem Code mit
Zeit zu tun? Nutzt diese Bibliotheken!

Darüber hinaus ist Monitoring-Code Quellcode und es gelten dieselben Ansprüche,
wie an jeden anderen Anwendungscode auch:
[KISS](https://de.wikipedia.org/wiki/KISS-Prinzip);
[DRY](https://de.wikipedia.org/wiki/Don%E2%80%99t_repeat_yourself); Clean-Code;
[Designpatterns](https://de.wikipedia.org/wiki/Entwurfsmuster);
[Unit-Tests](https://dev.to/evybauer/5-simple-reasons-why-testing-code-is-important-3707)
& Co. DevOps bedeutet nicht nur, dass Devs mehr Ops auf dem Schirm haben,
sondern auch umgekehrt.
