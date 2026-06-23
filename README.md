# Wordle Solver

Tekninen Python-pohjainen Wordle-ratkaisija. Projekti suodattaa mahdollisia vastaussanoja Wordle-palautteen perusteella, poistaa jo aiemmin käytettyjä vastauksia ja pisteyttää jäljelle jäävät kandidaatit kirjainten sekä sijaintien informaatioarvon perusteella.

Ratkaisija ei pelaa Wordleä automaattisesti selaimessa. Se on komentoriviltä ajettava analyysityökalu, jonka syöte annetaan muokkaamalla `src/main.py`-tiedoston listoja.

## Sisältö

- [Vaatimukset](#vaatimukset)
- [Asennus ja ajo](#asennus-ja-ajo)
- [main.py:n käyttö](#mainpyn-käyttö)
- [Syöteformaatit](#syöteformaatit)
- [Miten algoritmi toimii](#miten-algoritmi-toimii)
- [OSINT-tyylinen datan rikastaminen](#osint-tyylinen-datan-rikastaminen)
- [Pisteytys](#pisteytys)
- [Projektin rakenne](#projektin-rakenne)
- [Vianhaku](#vianhaku)

## Vaatimukset

- Python 3.9 tai uudempi
- Ei ulkoisia Python-kirjastoja
- Ajo repositorion juuresta, koska datatiedostojen polut ovat suhteellisia:
  - `storage/public/wordlist.txt`
  - `storage/public/wordlist2.txt`
  - `storage/public/wordle_answers.csv`

## Asennus ja ajo

Kloonaa repositorio:

```bash
git clone https://github.com/Svinte/Wordle-Solver.git
cd Wordle-Solver
```

Aja ohjelma:

```bash
python src/main.py
```

Joissain ympäristöissä komento on:

```bash
python3 src/main.py
```

Windowsissa vaihtoehtoisesti:

```powershell
py -3 src\main.py
```

Ohjelma tulostaa:

1. jäljellä olevien mahdollisten vastausten määrän
2. ensimmäiset 30 kandidaattia
3. kandidaattilistan yleisimmät kirjaimet
4. viisi parhaiten pisteytettyä sanaa

Tulosteen rakenne:

```text
Possible words: <määrä>
[<kandidaatteja>]
Letter frequencies:
<kirjain>: <määrä>

Top scored words:
<sana>: <pisteet>
```

## main.py:n käyttö

Avaa `src/main.py` ja muokkaa kolmea listaa:

```python
guesses = [
    # esim. ("irate", "bybbg")
]

comparing = [
    # esim. "bggby"
]

contains = [
    # esim. "a|b|c**1"
]
```

Tyypillinen käyttötapa:

1. Pelaa Wordlessä ensimmäinen sana.
2. Lisää arvaus ja Wordlen antama palaute `guesses`-listaan.
3. Aja `python src/main.py`.
4. Pelaa jokin `Top scored words` -listan sanoista.
5. Lisää uusi palaute `guesses`-listaan ja aja ohjelma uudelleen.

Esimerkki:

```python
guesses = [
    ("irate", "bybbg"),
    ("scone", "bbgbb"),
]

contains = [
    "r",
    "e",
]

comparing = []
```

Aja tämän jälkeen:

```bash
python src/main.py
```

## Syöteformaatit

### `guesses`

`guesses` sisältää tavalliset Wordle-arvaukset ja niihin saadut palautekuviot.

```python
guesses = [
    ("irate", "bybbg"),
]
```

Palautemerkit:

| Merkki | Merkitys | Tekninen tulkinta |
|---|---|---|
| `g` | green | kirjain on oikeassa kohdassa |
| `y` | yellow | kirjain on sanassa, mutta väärässä kohdassa |
| `b` | black/gray | kirjain ei ole sanassa, tai kyseistä kirjainta ei ole enempää jäljellä |

Säännöt:

- arvauksen pitää olla 5 kirjainta
- palautteen pitää olla 5 merkkiä
- käytä pieniä kirjaimia
- palaute saa sisältää vain merkkejä `g`, `y` ja `b`

### `contains`

`contains` on manuaalinen lisäsuodatin tilanteisiin, joissa haluat kuvata kirjainjoukkoihin liittyvää tietoa.

| Sääntö | Merkitys |
|---|---|
| `"a"` | sanassa pitää olla kirjain `a` |
| `"a|b|c"` | sanassa pitää olla vähintään yksi kirjaimista `a`, `b` tai `c` |
| `"a|b|c*2"` | sanassa pitää olla vähintään kaksi eri kirjainta joukosta `a`, `b`, `c` |
| `"a|b|c**2"` | sanassa pitää olla täsmälleen kaksi eri kirjainta joukosta `a`, `b`, `c` |

Huomio: `*` ja `**` laskevat eri kirjainten osumia annetusta joukosta, eivät saman kirjaimen toistokertoja sanassa.

### `comparing`

`comparing` on metatason suodatin. Se ei tarkoita yksittäistä arvausta samalla tavalla kuin `guesses`, vaan palautekuvion esiintyvyyttä suhteessa koko sallittujen arvausten listaan.

Esimerkki:

```python
comparing = [
    "bggby",
    "yybbb*3",
]
```

Tulkinta:

- `"bggby"` tarkoittaa, että kandidaatin pitää olla sellainen, että vähintään yksi sana `wordlist2.txt`-listasta tuottaisi kandidaattia vasten palautteen `bggby`.
- `"yybbb*3"` tarkoittaa, että vähintään kolmen sanan pitää tuottaa kandidaattia vasten palautekuvio `yybbb`.

Tätä voi käyttää silloin, kun halutaan hyödyntää palautekuvioiden rakennetta eikä vain yksittäisen arvauksen suoraa kirjaininformaatiota.

## Miten algoritmi toimii

`src/main.py` tekee seuraavan putken:

```text
wordlist.txt            -> mahdolliset vastaukset
wordlist2.txt           -> kaikki sallitut arvaukset
wordle_answers.csv      -> aiemmat Wordle-vastaukset

a answers - past_answers
        |
        v
contains-suodatus
        |
        v
guesses-suodatus
        |
        v
comparison-suodatus
        |
        v
kirjainfrekvenssit + pisteytys
        |
        v
top-kandidaatit
```

Käytännössä:

1. `src/main.py` lukee kaikki sallitut arvaukset tiedostosta `storage/public/wordlist2.txt`.
2. Se lukee mahdolliset vastaukset tiedostosta `storage/public/wordlist.txt`.
3. Se lukee aiemmat Wordle-vastaukset tiedostosta `storage/public/wordle_answers.csv`.
4. Se poistaa aiemmat vastaukset kandidaattilistasta.
5. Se ajaa `contains`-säännöt.
6. Se ajaa tavalliset Wordle-palautesäännöt `guesses`-listasta.
7. Se ajaa metatason `comparing`-säännöt.
8. Se laskee jäljellä olevien kandidaattien kirjain- ja sijaintipohjaiset pisteet.

## OSINT-tyylinen datan rikastaminen

Tässä projektissa OSINT-tyylisyys tarkoittaa havaintojen rikastamista: yksittäistä raakapalautetta ei käsitellä vain värinä, vaan siitä muodostetaan rakenteellisia sääntöjä, joita voidaan yhdistää muihin avoimiin sanalistoihin ja historialliseen vastausdataan.

Raakadata:

```python
("irate", "bybbg")
```

Rikastettu data:

| Palautetyyppi | Raakahavainto | Rikastettu tulkinta |
|---|---|---|
| vihreä `g` | kirjain osui | oikea kirjain oikeassa indeksissä |
| keltainen `y` | kirjain on mukana | kirjain kuuluu sanaan, mutta ei tähän indeksiin |
| harmaa `b` | kirjain hylättiin | kirjain puuttuu tai ylimääräinen esiintymä puuttuu |
| sanalista | mahdollinen vastausjoukko | hypoteesiavaruus |
| aiemmat vastaukset | historiallinen data | kandidaatit, joita ei oletuksena enää käytetä |
| palautekuviot | `bggby`, `yybbb` jne. | metatason signaaleja kandidaatin käyttäytymisestä eri arvauksia vasten |

Algoritmi toimii siksi samalla periaatteella kuin OSINT-analyysiputki:

```text
havainto -> normalisointi -> sääntö -> hypoteesien poissulku -> rikastetut piirteet -> priorisoitu arvio
```

### 1. Havainto

Wordlen antama palaute on havainto. Esimerkiksi:

```python
("irate", "bybbg")
```

Tämä ei vielä ole suoraan ratkaisu, vaan signaali.

### 2. Normalisointi

Koodi muuntaa sanalistojen sanat pieniksi kirjaimiksi ja hyväksyy vain 5-merkkiset sanat. Tämä yhtenäistää lähdedatan ennen analyysiä.

### 3. Säännöiksi muuttaminen

`_filter.py` muuntaa palautteen loogisiksi ehdoiksi:

- vihreä lukitsee kirjaimen tiettyyn indeksiin
- keltainen vaatii kirjaimen esiintymisen mutta estää saman indeksin
- harmaa poistaa kirjaimen, jos sen sallittu määrä on jo käytetty vihreissä ja keltaisissa osumissa

Toistuvat kirjaimet käsitellään `Counter`-laskurilla. Ensin kulutetaan vihreät osumat, sitten keltaiset, ja lopuksi harmaat tarkistetaan jäljellä olevasta kirjainmäärästä. Tämä estää yleisen Wordle-virheen, jossa yksi harmaa kirjain tulkitaan väärin koko kirjaimen täydelliseksi puuttumiseksi, vaikka samaa kirjainta olisi jo osunut vihreänä tai keltaisena.

### 4. Hypoteesiavaruuden pienentäminen

Jokainen sana `wordlist.txt`-tiedostossa on hypoteesi. Jos sana rikkoo yhdenkin säännön, se poistetaan.

Lopputulos ei ole enää pelkkä Wordle-väri, vaan pienempi joukko mahdollisia vastauksia.

### 5. Metatason vertailu

`comparing` vie analyysin yhden tason ylemmäs. Sen sijaan, että tarkistettaisiin vain tietyn arvauksen palaute, koodi simuloi palautekuvioita kandidaattia vasten kaikilla sallituilla arvaussanoilla.

Tämä muuttaa kysymyksen muodosta:

```text
Sopiiko tämä sana havaittuun palautteeseen?
```

muotoon:

```text
Tuottaako tämä kandidaatti samanlaisen palautekuvioiden profiilin kuin havainto edellyttää?
```

Siksi `comparing` toimii enemmän metadatana kuin suorana kirjainsääntönä.

### 6. Priorisointi

Kun kandidaatit on suodatettu, jäljellä olevia sanoja ei palauteta satunnaisessa järjestyksessä. Ne pisteytetään sen mukaan, miten hyvin ne kattavat jäljellä olevan kandidaattilistan yleisiä kirjaimia ja sijainteja.

## Pisteytys

Pisteytys tehdään `src/_score.py`-tiedostossa.

### Yellow frequency

`yellow_frequency` laskee, kuinka monessa jäljellä olevassa kandidaatissa kukin kirjain esiintyy. Sama kirjain lasketaan vain kerran per sana.

Tämä suosii sanoja, joiden kirjaimet kattavat mahdollisimman paljon jäljellä olevaa hakutilaa.

### Green frequency

`green_frequency` laskee, kuinka hyvin sanan kirjaimet esiintyvät samoissa kohdissa muiden kandidaattien kanssa.

Jos monessa jäljellä olevassa sanassa on sama kirjain samassa kohdassa, kyseinen sijainti kasvattaa pisteitä.

### Kokonaispisteet

`score_words` laskee kokonaispisteen näin:

```text
total_score = yellow_score * yellow_weight + green_score * green_weight
```

Oletuksena molemmat painot ovat `1.0`.

Huomio: pisteytys suosittelee parhaita vastauskandidaatteja jäljellä olevasta vastausjoukosta. Se ei tee täyttä entropiapohjaista Wordle-strategiaa eikä valitse testiarvauksia kandidaattilistan ulkopuolelta.

## Projektin rakenne

```text
Wordle-Solver/
├── README.md
├── LICENSE
├── src/
│   ├── main.py          # komentoriviltä ajettava pääohjelma
│   ├── _filter.py       # Wordle-palautteen ja comparison-sääntöjen suodatus
│   ├── _contains.py     # contains-sääntöjen käsittely
│   ├── _common.py       # kirjainfrekvenssit
│   └── _score.py        # kandidaattilistan pisteytys
└── storage/
    └── public/
        ├── wordlist.txt          # mahdolliset Wordle-vastaukset
        ├── wordlist2.txt         # kaikki sallitut arvaussanat
        └── wordle_answers.csv    # aiemmat Wordle-vastaukset
```

## Vianhaku

| Oire | Todennäköinen syy | Korjaus |
|---|---|---|
| `FileNotFoundError` | ohjelma ajettiin väärästä hakemistosta | aja komento repositorion juuresta: `python src/main.py` |
| `Invalid rule` | `comparing`-sääntö ei ole muodossa `gybgy` tai `gybgy*2` | tarkista, että sääntö on 5 merkkiä ja sisältää vain `g`, `y`, `b` |
| `No valid candidates found` | säännöt ovat ristiriidassa | poista viimeisin sääntö tai tarkista Wordle-palautteen merkit |
| `IndexError` | arvaus tai palaute ei ole 5 merkkiä | varmista, että jokainen `guess` ja `result` on täsmälleen 5 merkkiä |
| tulokset vaikuttavat vääriltä | käytössä on isoja kirjaimia syötteissä | käytä `guesses`, `contains` ja `comparing` -listoissa pieniä kirjaimia |
| vanha Wordle-arkistovastaus ei näy kandidaateissa | `wordle_answers.csv` poistaa aiemmin käytetyt vastaukset | tyhjennä tai muokkaa historiallisen vastausdatan suodatusta, jos ratkaiset arkistopelejä |

## Lisenssi

MIT License.
