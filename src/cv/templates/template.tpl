<html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="css/styles.css">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:200,400,600,800&display=swap" rel="stylesheet">
        <style>
            * {
              margin: 0;
            }

            body {
              font-family: 'Montserrat', sans-serif;
            }

            .container {
              margin: 0 10px;
              margin-top: 15px;
            }

            header {
              text-align: center;
              margin: 20px;
            }

            h2 {
              text-align: left;
              font-weight: 400;
              border-bottom: 1px solid grey;
              margin: 0.5rem 0;
            }

            h3 {
              font-weight: 600;
              margin: 0.5rem 0;
            }

            h4 {
              font-weight: 400;
              margin: 0.5rem 0;
            }

            p {
              margin: 0.5rem 0;
            }

            .item {
              margin-left: 25%;
              padding: 10px 0;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>{{basic_info.name}} {{basic_info.surname}}</h1>
            <p><b>Data urodzenia: </b>{{basic_info.date_of_birth}}</p>
            <p><b>Telefon: </b>{{basic_info.telephone}}</p>
            <p><b>E-mail: </b>{{basic_info.email}}</p>
        </header>

        <div class="container" id="education">
            <h2>Wykształcenie</h2>
            {% for item in education %}
            <div class="item">
                <h3>{{item.place}}</h3>
                <h4>{{item.date_start}} - {% if item.date_end %}{{item.date_end}}{% else %}...{% endif %}</h4>
                <p>{{item.additional_info}}</p>
            </div>
            {% endfor %}
        </div>

        <div class="container" id="experience">
            <h2>Doświadczenie</h2>
            {% for item in experience %}
            <div class="item">
                <h3>{{item.place}}</h3>
                <h4>{{item.date_start}} - {% if item.date_end %}{{item.date_end}}{% else %}...{% endif %}</h4>
                <p>{{item.additional_info}}</p>
            </div>
            {% endfor %}
        </div>

        <div class="container" id="skills">
            <h2>Umiejętności</h2>
            <p class="item">
                {% for item in skills %}
                {{item}},
                {% endfor %}
            </p>
        </div>
        
        <div class="container" id="languages">
            <h2>Języki</h2>
            <p class="item">
                {% for item in languages %}
                {{item}},
                {% endfor %}
            </p>
        </div>

        <div class="container" id="klauzula">
            <p>
            Wyrażam zgodę na przetwarzanie moich danych osobowych dla potrzeb niezbędnych do realizacji
            procesu rekrutacji (zgodnie z ustawą z dnia 10 maja 2018 roku o ochronie danych osobowych 
            (Dz. Ustaw z 2018, poz. 1000) oraz zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 
            2016/679 z dnia 27 kwietnia 2016 r. w sprawie ochrony osób fizycznych w związku z przetwarzaniem 
            danych osobowych i w sprawie swobodnego przepływu takich danych oraz uchylenia dyrektywy 95/46/WE (RODO)).
            </p>
        </div>
    </body>
</html>