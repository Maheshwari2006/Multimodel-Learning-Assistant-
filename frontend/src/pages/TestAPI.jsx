import { useEffect } from "react";

import api from "../api/api";

function TestAPI() {

    useEffect(() => {

        api.get("/")

        .then((res) => {

            console.log(res.data);

        })

        .catch((err) => {

            console.log(err);

        });

    }, []);

    return (

        <h1>

            Backend Connected Successfully

        </h1>

    );

}

export default TestAPI;