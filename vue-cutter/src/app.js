import { ref, computed } from 'vue'
import axios from 'axios';

// Global Functions & Variables
export const host = ref(window.location.host)
export const protocol = ref(window.location.protocol)    

// Leading Zero's
export const zeroPad = (num, places) => String(num).padStart(places, '0')


// ************************************************************************************************
// posistion in movie, get frame @ position
// ************************************************************************************************
export const lpos = ref(0)

// computed variabel pos ... loads frame @ movie position 
export const pos = computed({
    get: () => {
            //console.log("in pos getter ", lpos.value)
            const spos = pos2str(lpos.value)
            get_frame(spos)
            return spos
        },
    set: (newValue) => {
            //console.log("in pos setter ", newValue)
            lpos.value = str2pos(newValue)
        }
})

export const frame_name = ref('');
export async function get_frame(pos) {
    const endpoint = `${protocol.value}//${host.value}/frame`
    // console.log(`in load frame, Position ${pos}`)
    try {
        const response = await axios.post(endpoint,
            { "pos_time": pos, "movie_name": movie.value },
            { headers: { 'Content-type': 'application/json', }});
        frame_name.value = response.data.frame + '?' + String(Math.random());
        // toggle_timeline.value = false  
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

export const hpos = (b) => {
    // this.toggle_timeline = false 
    if (b.type == "rel") {
        set_timeline_step(Math.abs(b.val))
        if (!toggle_timeline.value) {
            lpos.value += b.val
            lpos.value = posvalid(lpos.value)
            // console.log(this.lpos)
        }
        timeline(lpos.value)                
    } else if (b.type == "abs") {
        //console.log('in hpos type abs', b)
        lpos.value = b.val
        timeline(lpos.value)                 
    } else if (b.type == "t0")  {
        t0.value = pos.value
        t0_valid.value = true 
    }else if (b.type == "t1")  {
        t1.value = pos.value
        t1_valid.value = true 
    } else {
        alert("unknown type in hpos")
    }

}

// seconds to 'hh:mm:ss' string
export const pos2str = (pos) => {
    pos = (pos >= 0) ? pos : 0 
    return `${zeroPad(Math.trunc(pos / 3600),2)}:${zeroPad(Math.trunc((pos % 3600) / 60),2)}:${zeroPad(Math.trunc(pos % 60,2),2)}`
}

// 'hh:mm:ss' string to seconds
export const str2pos = (st) => {
    let erg = parseInt(String(st).slice(0,2))*3600 + parseInt(String(st).slice(3,5))*60 + parseInt(String(st).slice(-2))
    return erg
}

export const pos_from_end = (dsec) => {
    let val = Math.trunc(lmovie_info.value.duration_ms / 1000 - dsec) 
    val = (val < 0) ? 0 : val
    return val
}

export const posvalid = (val) => {
    val = (val >=0 ) ? val : -998 //0
    val = (val <= pos_from_end(0)) ? val : -998 //this.pos_from_end(0)
    return val
}



// ************************************************************************************************
// timeline functions
// ************************************************************************************************
export const toggle_timeline = ref(false)
export const ltimeline = ref({
    basename: 'frame.gif',
    larray: [],
    pos: 0,
    l: -4,
    r: 4,
    step: 1,
    size: '160'
})

export function pos2fname(pos) {
    if (pos === -999) {
        return '/static/spinner_160x90.gif'
    } else if (pos === -998) {
        return '/static/background.png'
    } else  {
        return  '/static/' + ltimeline.value.basename.slice(0,-4) + '_' + pos2str(pos) + ltimeline.value.basename.slice(-4) + '?' + String(Math.random())
    }
}

export const set_timeline_step = (step) => {
    ltimeline.value.step = step
    lpos.value = Math.trunc(lpos.value / step) * step
}

export const timeline = async (mypos) => {
    const endpoint = `${protocol.value}//${host.value}/timeline`
    if (toggle_timeline.value) {
        ltimeline.value.larray.length = 0
        for (let p=ltimeline.value.l;p<=ltimeline.value.r;p+=1) {
            ltimeline.value.larray.push(-999)
        }
        // const sarray = []
        try {
            const response = await axios.post(endpoint,
                { 
                    "basename": ltimeline.value.basename,
                    "pos": mypos,
                    "l": ltimeline.value.l,
                    "r": ltimeline.value.r,
                    "step": ltimeline.value.step,
                    "size": ltimeline.value.size
                },
                { headers: {
                    'Content-type': 'application/json',
                }
            })
            //console.log('promise timeline resolved', response.data)
            ltimeline.value.larray.length = 0
            for (let p=ltimeline.value.l;p <=ltimeline.value.r;p+=1) {
                let val = mypos + p*Math.abs(ltimeline.value.step)
                val = posvalid(val)
                ltimeline.value.larray.push(val)
                // sarray.push(pos2fname(val))
            }
            //console.log(ltimeline.value.larray)
            //console.log(sarray)
        } catch (e) {
            console.log(`${endpoint} \n` + String(e));
            alert(`${endpoint} \n` + String(e));
        }

    }
}


export const sections = ref([])
export const section = ref('')
export const section_type = ref('')
export const movies = ref([])
export const lmovie = ref('')
export const seasons = ref([])
export const season = ref('')
export const series = ref([])
export const serie = ref('')

export const lmovie_info = ref({})

export const t0 = ref("00:00:00")
export const t0_valid = ref(false)
export const t1 = ref("01:00:00")
export const t1_valid = ref(false)
export const inplace = ref(true) 


export function reset_t0_t1() {
    t0.value = "00:00:00"
    t0_valid.value = false 
    t1.value = "01:00:00"
    t1_valid.value = false                 
}

// computed:
export const movie = computed({
    get: () => {
        //reset_t0_t1()
        lpos.value = 0
        //timeline(lpos.value)
        //this.lmovie_dummy = this.lmovie_dummy
        load_movie_info()
        return lmovie.value
    },
    set(val) {
        //console.log('in movie setter')
        lmovie.value = val
    }
})




// methods:
export async function load_movie_info() {
    const endpoint = `${protocol.value}//${host.value}/movie_info`
    /* console.log(
        'url:', endpoint, 
        'section:', section.value, 
        'lmovie', lmovie.value
    ) */
    try {
        const response = await axios.post(endpoint,
            { "section": section.value, "movie": lmovie.value },
            { headers: { 'Content-type': 'application/json', }});
        // console.log('response', response.data)
        lmovie_info.value = response.data.movie_info
        // console.log('lmovie_info', lmovie_info.value)
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

export const progress_status = ref({
    "apsc_size": 0,
    "progress": 0,
    "started": 0,
    "status": "idle",
    "title": "-"
  })