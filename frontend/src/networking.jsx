import request from 'superagent';
import cookie from 'react-cookie';


function handle(callback) {
    return function (err, response){
        if (err) {
            console.log("error:", err);
        }
        if (response) {
            console.log(response);
        }
        if (err !== null && parseInt(err.status) == 401 && getToken().length > 8) {
            location.href = '/logout'
        } else if (response && response.body){
            callback(response.body, err);
        }
    }
}

function getToken() {
    return cookie.load('bellyfeel_token');
}

class APIClient {
    constructor() {
    }
    doGET(path, callback){
        return request.get(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .end(handle(callback));

    }
    doPOST(path, payload, callback) {
        return request.post(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send(payload)
                      .end(handle(callback));
    }
    doPUT(path, payload, callback) {
        return request.put(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send(payload)
                      .end(handle(callback));
    }
    doDELETE(path, callback) {
        return request.delete(path)
                      .set('Authorization', "Bearer: " + getToken())
                      .set('Accept', 'application/json')
                      .send()
                      .end(handle(callback));
    }

    authenticate(callback) {
        return this.doGET('/api/user', callback);
    }
    triggerNewBuild(id, callback){
        return this.doPOST('/api/build', {"project_id": id}, callback);
    }
    getBuildById(id, callback) {
        return this.doGET('/api/build/' + id, callback);
    }
    getProjectById(id, callback) {
        return this.doGET('/api/project/' + id, callback);
    }
    retrieveProjects(callback) {
        return this.doGET('/api/projects',callback);
    }
    retrieveOrganizationRepos(name, callback) {
        return this.doGET('/api/github/repos/' + name, callback);
    }
    retrieveUserRepos(callback) {
        return this.doGET('/api/github/repos', callback);
    }
    importProject(name, callback) {
        return this.doPOST('/api/project/import', {"name": name}, callback);
    }
    editProject(id, data, callback) {
        return this.doPUT('/api/project/' + id, data, callback);
    }
    deleteProject(id, callback) {
        return this.doDELETE('/api/project/' + id, callback);
    }
    deleteBuild(id, callback) {
        return this.doDELETE('/api/build/' + id, callback);
    }

}

export default APIClient
