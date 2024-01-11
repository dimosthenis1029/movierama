<template>
  <div style="text-align:left"  >
    <h1 class="bb">  {{ msg }}</h1>
    <body v-if="logged_in=='false'" style="text-align:right">
      Please login or sign up to insert or like movie:  
      User:
      <input type="text" v-model="insert_user">
      Password:
      <input type="text" v-model="password">
      <button @click="log_in" >Log In</button>
      or
      <button @click="sing_up" >Sign Up</button>
    </body>
    <body v-if="logged_in=='true'" style="text-align:right">
      Hey, {{this.insert_user}}!
      <button @click="log_out" >Log Out</button>
    </body>
    <body v-if="logged_in=='true'">
      Insert new movie: Title: 
      <input type="text" v-model="title">
      Description:
      <input type="text" v-model="description">
      <button @click="insert_movie" >Insert</button>
      </body>
    <body>
    
    Sort by: 
    <button @click="sort_by_likes" >Likes</button>
    <button @click="sort_by_hates" >Hates</button>
    <button @click="sort_by_date" >Date</button>

    </body>
      <div v-for="item in movies" :key="item.title">
        <body>
          <table border="2" bordercolor="#336699" cellpadding="2" cellspacing="2" width="60%">
          <h1>{{ item.title }}</h1>
          <tr>Posted by <button @click="filter_by_user(item)" >{{item.user}}</button> {{ item.date[0]}} days and {{ item.date[1]}} hours ago</tr>
          <tr>{{ item.description }}</tr>
          <tr>{{ item.likes }} Likes | {{ item.hates }} Hates</tr>
          <tr style="color:green" v-if="item.like_users.includes(insert_user) & logged_in=='true'">You like this</tr>
          <tr style="color:red" v-if="item.hate_users.includes(insert_user) & logged_in=='true'">You hate this</tr>
          <button v-if="logged_in=='true'" @click="like(item)" >Like</button>
          <button v-if="logged_in=='true'" @click="hate(item)" >Hate</button>
          </table>
        </body>
      </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'HelloWorld',
  props: {
    msg: String
  },
  data() {
    return {
      user: '',
      password: '',
      insert_user:'',
      logged_in : 'false',
      sort: '',
      title: '',
      description: '',
      opinion_user: '',
      opinion: '',
      movies:[]
    }
  },
  methods: {
    log_in(){
      this.insert_user = this.insert_user.toUpperCase()
      this.logged_in = 'true'
    },
    sing_up(){
      this.insert_user = this.insert_user.toUpperCase()
      this.logged_in = 'true'
    },
    log_out(){
      this.logged_in = 'false'
      this.insert_user = ''
      this.password = ''
    },
    like(item){
      axios.post("http://ec2-52-91-51-228.compute-1.amazonaws.com:5002/opinion_movie", {"title":item.title,"opinion_user":this.insert_user,"opinion":"like"}).then(() => {
        this.search_movies()
      });
    },
    hate(item){
      axios.post("http://ec2-52-91-51-228.compute-1.amazonaws.com:5002/opinion_movie", {"title":item.title,"opinion_user":this.insert_user,"opinion":"hate"}).then(() => {
        this.search_movies()
      });
    },
    insert_movie(){
      axios.post("http://ec2-52-91-51-228.compute-1.amazonaws.com:5002/insert_movie", {"title":this.title,"description":this.description,"user":this.insert_user}).then(() => {
        this.title = ''
        this.description = ''
        this.user = ''
        this.search_movies()
      });
    },
    sort_by_likes(){
      this.sort = 'likes'
      this.search_movies()
    },
    sort_by_hates(){
      this.sort = 'hates'
      this.search_movies()
    },
    sort_by_date(){
      this.sort = 'date'
      this.search_movies()
    },
    filter_by_user(item){
      if(item.user==this.user){
        this.user=''
        this.search_movies()
      } else{
       this.user = item.user
       this.search_movies()
      }
    },
    search_movies() {
      axios.post("http://ec2-52-91-51-228.compute-1.amazonaws.com:5002/get_movies", {"user":this.user,"sort":this.sort}).then((response) => {
            this.movies = response.data.data
          })
          .catch(err=>{
            console.log(err)
          });
      }
  },
  mounted() {
    this.search_movies();
  }
}
</script>

<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.bb {
    border-bottom: 1px solid #999;
    padding-bottom: 10px;
    padding-top: 10px;
    padding-left: 10px;
    background-color: rgb(183, 141, 82);
    overflow: hidden;
}
</style>
