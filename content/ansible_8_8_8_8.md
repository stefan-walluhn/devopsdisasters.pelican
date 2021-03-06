Title: Alle Wege führen nach 8.8.8.8
Date: 2022-02-24 21:23
Category: CI/CD
Tags: Ansible, Deployment
Quote: Well it begins, as it must, with our mutual friend - Ansible
Summary: Über Ansibles kreativen Ansatz, ein Default-Interface zu finden und der sich daraus ergebenden Frage, was ein Default-Interface eigentlich ist.

Ansible kennt einen länglichen Satz an Fakten über einen bestimmten Node. Nach
der Verbindung zu einem Node sorgt ein sogenanntes "fact gathering" dafür,
diese facts in Erfahrung zu bringen. So gibt es beispielsweise einen fact
`ansible_all_ipv4_addresses` mit der Liste aller IPv4-Adressen. Mit dem Befehl
`ansible -m setup localhost` lässt sich einfach eine Liste aller lokalen facts
abrufen.

Ein weiterer fact nennt sich `ansible_default_ipv4`, unter dem sich diverse
Informationen zur Default-IPv4-Adresse finden.

    :::yaml
    "ansible_default_ipv4": {
        "address": "192.168.121.108",
        "broadcast": "192.168.121.255",
        "gateway": "192.168.121.1",
        "interface": "eth0",
        "mtu": 1500,
        "netmask": "255.255.255.0",
        "network": "192.168.121.0",
        "type": "ether"
    }

So nützlich dieser fact ist, es stellt sich die Frage: Was genau ist denn
eigentlich die Default-IPv4-Adresse? Einem Node können mehrere IP-Adressen
zugewiesen sein. Welche dieser Adressen ist die Default-Adresse? Meine
Erwartung wäre, dass es sich dabei um jene IP-Adresse handelt, die zum
Default-Gateway, und damit zur Default-Route zeigt. Wenn dem so wäre, was ist
dann mit Nodes, die keine Default-Route eingerichtet haben (ja, das gibt es
wirklich)?

Ansible beantwortet diese Frage, nun ja, nennen wir es einfach
"kreativer" [^ansible_code]:

    :::python
    def get_default_interfaces(self, ip_path, collected_facts=None):
            collected_facts = collected_facts or {}
            # Use the commands:
            #     ip -4 route get 8.8.8.8                     -> Google public DNS
            #     ip -6 route get 2404:6800:400a:800::1012    -> ipv6.google.com
            # to find out the default outgoing interface, address, and gateway
            command = dict(
                v4=[ip_path, '-4', 'route', 'get', '8.8.8.8'],
                v6=[ip_path, '-6', 'route', 'get', '2404:6800:400a:800::1012']
            )

[^ansible_code]:<https://github.com/ansible/ansible/blob/stable-2.10/lib/ansible/module_utils/facts/network/linux.py#L64-L74>

Augen gerieben? Jaja, richtig gelesen. Die Route, die auf 8.8.8.8 zeigt, ist
die Default-Route und das dazugehörige Interface ist das Default-Interface. So
sieht das zumindest Ansible. Ihr wollt, dass Ansible ein anderes Interface als
Default-Interface erkennt? Kein Problem, einfach eine Host-Route setzen:

    :::console
    $ ip route add "8.8.8.8/32" via "127.0.0.1"

Voila:

    :::yaml
    "ansible_default_ipv4": {
        "interface": "lo",
    }

Bleibt die Frage, was eigentlich auf Nodes passiert, die keine Route nach
8.8.8.8 gesetzt haben...

Solche Stunts finden sich an verschiedenen Stellen im Ansible-Code. Aber wie
sähe eine korrekte Antwort aus? Das Grundproblem ist, dass es im IP-Stack zwar
einen Default-Gateway, aber keine Definition eines Default-Interfaces gibt. Nun
braucht man bei der Automatisierung von Infrastruktur trotzdem immer wieder
dieses eine Interface, welches irgendwie Default zu einem Node gehört. Dennoch
bleibt das Dilemma, dass diese Frage für einzelne Nodes, beispielsweise für
dynamische Router, schwer bis gar nicht zu beantworten ist.

Ich würde erwartet, dass das Default-Interface jenes ist, welches zum
Default-Gateway zeigt. Auf manchen Nodes gibt es nach dieser Definition kein
Default-Interface, der entsprechende fact müsste also leer bleiben oder - noch
besser - beim Zugriff eine Exception werfen, damit ich in meinem Ansible-Code
merke, dass ich hier gerade Mist baue.

## Lessons learned?

Aus irgendeinem Grunde scheuen sich Entwickler:innen davor, ihren Code in
undefinierten Zuständen kontrolliert abschmieren zu lassen. Gerade
Anfänger:innen höre ich immer wieder Dinge sagen wie: aber dann stürzt das
Programm ab und ist instabil. Ja! Besser kontrolliert abschmieren, als in
undefinierten Zuständen das Falsche zu tun, inkonsistente Daten zu liefern oder
im schlimmsten Falle Datenbanken zu korrumpieren. Dafür gibt es Exceptions. Und
wenn es nicht möglich ist, eine Ausnahmesituation sinnvoll zu beantworten, dann
sollte ein Programm unbedingt aufhören, unter falschen Annahmen Dinge kaputt zu
machen.

Und wenn ich von Ansible Informationen zu einem Default-Interface brauche, ein
solches Interface auf einem bestimmten Node aber nicht zweifelsfrei bestimmt
werden kann, dann ist das eine genau solche Situation. Besser kontrolliert
abschmieren, als einen Service aus Versehen auf ein falsches Interface zu
binden und im schlimmsten Fall unerwartet in der falschen Firewall-Zone zu
exponieren.
