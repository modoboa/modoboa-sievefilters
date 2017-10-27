#####
Setup
#####

To use this extension, your hosting setup must include a *ManageSieve*
server and your local delivery agent must understand the *Sieve*
language. Don't panic, Dovecot supports both :-) (refer to
:ref:`modoboa:dovecot` to know how to enable those features).

Go the online panel and modify the following parameters in order to
communicate with the *ManageSieve* server:

+--------------------+--------------------+--------------------+
|Name                |Description         |Default value       |
+====================+====================+====================+
|Server address      |Address of your     |127.0.0.1           |
|                    |MANAGESIEVE server  |                    |
+--------------------+--------------------+--------------------+
|Server port         |Listening port of   |4190                |
|                    |your MANAGESIEVE    |                    |
|                    |server              |                    |
+--------------------+--------------------+--------------------+
|Connect using       |Use the STARTTLS    |no                  |
|STARTTLS            |extension           |                    |
+--------------------+--------------------+--------------------+
|Authentication      |Prefered            |auto                |
|mechanism           |authentication      |                    |
|                    |mechanism           |                    |
+--------------------+--------------------+--------------------+

You also need to indicate where your *IMAP* server is:

+--------------------+--------------------+--------------------+
|Name                |Description         |Default value       |
+====================+====================+====================+
|Server address      |Address of your IMAP|127.0.0.1           |
|                    |server              |                    |
+--------------------+--------------------+--------------------+
|Use a secured       |Use a secured       |no                  |
|connection          |connection to access|                    |
|                    |IMAP server         |                    |
+--------------------+--------------------+--------------------+
|Server port         |Listening port of   |143                 |
|                    |your IMAP server    |                    |
+--------------------+--------------------+--------------------+
