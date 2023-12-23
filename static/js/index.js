$(document).ready(function() {
    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");

    });

    var options = {
        slidesToScroll: 1,
        slidesToShow: 1,
        loop: true,
        infinite: true,
        autoplay: false,
        autoplaySpeed: 3000,
    }

		// Initialize all div with carousel class
    var carousels = bulmaCarousel.attach('.carousel', options);

    // Loop on each carousel initialized
    for(var i = 0; i < carousels.length; i++) {
    	// Add listener to  event
    	carousels[i].on('before:show', state => {
    		console.log(state);
    	});
    }

    // Access to bulmaCarousel instance of an element
    var element = document.querySelector('#my-element');
    if (element && element.bulmaCarousel) {
    	// bulmaCarousel instance is available as element.bulmaCarousel
    	element.bulmaCarousel.on('before-show', function(state) {
    		console.log(state);
    	});
    }

    var dropdowns = document.getElementsByClassName('dropdown');
    for (let dropdown of dropdowns) {
        dropdown.addEventListener('click', function(event) {
            event.stopPropagation();
            event.preventDefault();
            dropdown.classList.toggle('is-active');
        });
    }

    // load and display default models
    let qids = getRandomSubarray(num_output_qs);
    let [folder , output_data] = read_data('Multimodal Bard');
    output_data.addEventListener('load', function() {
        refresh_table(qids);
    });
    [folder , output_data] = read_data('CoT GPT4 (Caption + OCR)');
    output_data.addEventListener('load', function() {
        refresh_table(qids);
    });
    // refresh_table(qids);
    let dropdown_displays = document.getElementsByClassName('dropdown-display');
    let refresh_button = document.getElementById('refresh-qids');
    refresh_button.addEventListener('click', function(event) {
        qids = getRandomSubarray(num_output_qs);
        refresh_table(qids);
    });

    // let dropdown_displays = document.getElementsByClassName('dropdown-display');
    let dropdown_contents = document.getElementsByClassName('dropdown-content');
    for (let i = 0; i < dropdown_contents.length; i++) {
        // add an <a> tag to the dropdown-content for each key in name_to_folder_map
        let dropdown_content = dropdown_contents[i];
        for (let name in name_to_folder_map) {
            let a = document.createElement('a');
            a.classList.add('dropdown-item');
            a.innerHTML = '<b> ' + name + ' </b>';
            dropdown_content.appendChild(a);
            a.addEventListener('click', function(event) {
                dropdown_displays[i].innerHTML = name;
                let [folder, script_tag] = read_data(name);
                script_tag.addEventListener('load', function() {
                    refresh_table(qids);
                });
            });
            a.style.padding = '0.375em 1em';
        }
    }

    // create the leaderboard
    let leaderboard = new Tabulator("#score-table", {
        data:score_table, //assign data to table
        layout:"fitDataTable",
        // layout:"fitColumns",
        initialSort:[
            {column:"ALL", dir:"desc"}, //sort by this first
        ],
        autoColumns:true, //create columns from data field names
    });
})

var cache = {};
var num_output_qs = 5;
// var 

// dynamically links a js data file
function read_data(model_name) {
    console.log('loading data for ' + model_name);
    let folder = name_to_folder_map[model_name];
    // dynamically link the js file
    let script = document.createElement('script');
    script.src = './data/results/' + folder + '/data.js';
    document.body.appendChild(script);
    return [folder, script];

}

function getRandomSubarray(size, arr=null) {
    if (arr == null) {
        arr = [];
        for (let i = 1; i < 1001; i++) {
            arr.push(i);
        }
    }
    var shuffled = arr.slice(0), i = arr.length, temp, index;
    while (i--) {
        index = Math.floor((i + 1) * Math.random());
        temp = shuffled[index];
        shuffled[index] = shuffled[i];
        shuffled[i] = temp;
    }
    return shuffled.slice(0, size);
}

function refresh_table(qids) {
    let table = document.getElementById('result-table');
    let dropdown_displays = document.getElementsByClassName('dropdown-display');
    let model_names = [];
    for (let i = 0; i < dropdown_displays.length; i++) {
        model_names.push(dropdown_displays[i].innerText);
    }
    console.log(qids);
    console.log(model_names);
    while (table.children.length > 3) 
        table.removeChild(table.lastChild);

    for (let qid of qids) {
        let row = generate_row(qid, model_names);
        // console.log('inserting' + row);
        table.insertAdjacentHTML('beforeend', row);
    }
}

function generate_row(qid, model_names) {
    let responses = [];
    for (let model_name of model_names) {
        if (model_name in cache)
            responses.push(cache[model_name][qid.toString()]);
        else
            responses.push({'response': ''});
    }
    let html = `
    <div class="level has-text-justified box question-level" style="background: rgba(0, 0, 0, 0.02);">
        <div class='leve-item container m-3' style='width: 30%;'>
            ${create_number(test_data[qid.toString()])}
        </div>
        <div class='leve-item container m-3' style='width: 30%; white-space: pre-wrap;'>${responses[0]['response']}</div>
        <div class='leve-item container m-3' style='width: 30%; white-space: pre-wrap;'>${responses[1]['response']}</div>
    </div>`;
    return html;
}