# ez-egy-projekt
Ez egy projekt

Megj: Valóban, ez egy projekt

## Előfeltételek
A játék futtatásához a következők szükségesek:
- Pyhton 3.10 or newer
- java 17 or newer
- py5 
Részletes telepítési útmutató: http://py5coding.org/content/install.html

A dámajáték programját a következő fájlok tartalmazzák:
- checkers.py
- game_pvp.py
- menu.py
- player_movement.py
- checkers_graphics.py

## Futtatás
A dámajátékot a checkers.py fájl elindításával tudjuk megkezdeni. Ekkor egy menü jelenik meg, ahol a választhatunk a lehetséges játékmódok közül.
![menu](./readme_pictures/menu.jpg)
A játékmód kiválasztása után a start gombra kattintva a játék elindul, és a következő képernyőre érkezünk:
![start screen](./readme_pictures/start.jpg)
Itt a bal felső sarokban azt látjuk, hogy éppen melyik játékos van soron (a lezajló animációk után). A jobb felső sarokban a szünet menü gombját találjuk, ez megállítja a játékot, és a következő menüt jeleníti meg:
![pause screen](./readme_pictures/pause_menu.jpg)
A "Folytatás" gombbal visszatérhetünk a játékba, míg a "Kilépés" gombbal befejezhetjük a játékot a menübe lépve.

A játék egy általános állapota a következőképp nézhet ki, itt a piros pöttyel megjelölt bábuk a dámák.
![generic state](./readme_pictures/generic.jpg)
Amennyiben az egyik játékosnak elfogynak a lépési lehetőségei, veszít. Ekkor a játék 3 másodpercig jelzi a nyertes játékost, majd visszakerülünk a menübe.
![end screen](./readme_pictures/end.jpg)

## Játékos lépése
Amikor játékoson van a sor, a játék megjelöli azon bábukat, melyekkel tud lépni. Ezt az ütéskényszer figyelembevételével teszi. A bábura kattintva a játék felajánlja a lépési lehetőségeket. Amennyiben nem egy lehetőségre kattintunk, megszakítjuk a bábu lépését, azaz újra választhatunk a mozogni képes bábuk közül.
![movement options](./readme_pictures/movement%20options.jpg)
![piece steps](./readme_pictures/piece%20step%20options.jpg)

Amennyiben lépésként kiválasztunk egy ütést, ütéssorozat indul meg. Itt addig kell választanunk lépést, amíg olyan pozícióba kerül a bábu, ahol már nem tud ütni. Az ütéssorozatot már nem tudjuk megszakítani, ha egyszer megkezdjük a lépést.
![capture](./readme_pictures/capture.gif)

## A bot taktikája
A bot döntését az alapján hozza, hogy végignézi saját és ellenfele lehetőségeit 3-3 lépéssel előre. Egyes lépések kiértékelése a kövekező módon történik:
- ütés: +1 pont
- dáma létrehozása: +1 pont 
- ellenfél üt: -1 pont
- ellenfél hoz létre dámát: -1 pont
- játék megnyerése: +100 pont
- játék elvesztése: -100 pont
A lépéssorozatokat a bot rekurzív módon értékeli ki, olyan módon, hogy mindkét játékos ezen pontozás szerint a lehető legoptimálisabban próbál lépni. Ez alapján választja ki saját lépését.

A bot működését demostrálja a következő bot vs. bot játék:
![full game](./readme_pictures/example_bot_run.gif)