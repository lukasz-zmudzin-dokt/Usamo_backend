<html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="css/styles2.css">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:200,400,600,800&display=swap" rel="stylesheet">
        <style>
            * {
              margin: 0;
            }

            body {
              font-family: 'Montserrat', sans-serif;
            }

            .container {
              margin: 0 10%;
            }

            header {
              background-color: lightblue;
              color: white;
              padding: 30px;
              margin-bottom: 70px;
              padding-right: 10%;
              padding-left: 10%;
              padding-top: 10%;
            }

            h2 {
              text-align: left;
              font-weight: 600;
              border-bottom: 1px solid grey;
              margin-top: 2rem;
              margin-bottom: 0.5rem;
            }

            #name {
              font-size: 4rem;
              text-align: left;
              width: 60%;
              display: inline-block;
            }

            #contact {
              display: inline-block;
            }

            h3 {
              font-weight: 600;
              margin-bottom: 0.5rem;
            }

            h4 {
              font-weight: 200;
              margin-bottom: 0.5rem;
              text-align: right;
            }

            p {
              margin: 0;
            }

            .item {
              padding-bottom: 10px;
            }

            #klauzula {
              margin-top: 30px;
              margin-bottom: 30px;
              text-align: justify;
            }
        </style>
    </head>
    <body>
        <header>
            <h1 id="name">{{basic_info.first_name}}</br>{{basic_info.last_name}}</h1>
            <div id="contact">
                <p><b>Data urodzenia: </b></br>ur. {{basic_info.date_of_birth}}</p>
                <p><b>Telefon: </b></br>{{basic_info.phone_number}}</p>
                <p><b>E-mail: </b></br>{{basic_info.email}}</p>
            </div>
        </header>

        <div class="container" id="schools">
            <h2>Wykształcenie</h2>
            {% for item in schools %}
            <div class="item">
                <h4>{{item.year_start}} - {% if item.year_end %}{{item.year_end}}{% else %}...{% endif %}</h4>
                <h3>{{item.name}}</h3>
                <p>{{item.additional_info}}</p>
            </div>
            {% endfor %}
        </div>

        <div class="container" id="experiences">
            <h2>Doświadczenie</h2>
            {% for item in experiences %}
            <div class="item">
                <h4>{{item.year_start}} - {% if item.year_end %}{{item.year_end}}{% else %}...{% endif %}</h4>
                <h3>{{item.title}}</h3>
                <p>{{item.description}}</p>
            </div>
            {% endfor %}
        </div>

        <div class="container" id="skills">
            <h2>Umiejętności</h2>
            <p class="item">
                {% for item in skills %}
                {{item.description}},
                {% endfor %}
            </p>
        </div>

        <div class="container" id="languages">
            <h2>Języki</h2>
            <p class="item">
                {% for item in languages %}
                {{item.name}} - {{item.level}},
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