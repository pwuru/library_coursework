import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false,
        username: null
    })
    const otpStatus = ref({
        otp_good: false
    })

    async function checkLogin() {
        try {
            let r = await axios.get("/api/userProfiles/check-login/")
            userInfo.value = r.data;
        } catch (error) {
            userInfo.value = { is_authenticated: false, username: null }
        }
    }

    async function login(username, password) {
        await axios.post("/api/userProfiles/login/", {
            username: username,
            password: password,
        })
        await checkLogin();
    }

    async function logout() {
        await axios.post("/api/userProfiles/logout/", {}, {
            headers: {
                'X-CSRFToken': Cookies.get("csrftoken")
            }
        })
        userInfo.value = { is_authenticated: false, username: null }
        otpStatus.value = { otp_good: false }
    }

    async function verifyOTP(key) {
        let r = await axios.post("/api/userProfiles/otp-login/", { key }, {
            headers: {
                'X-CSRFToken': Cookies.get("csrftoken")
            }
        })
        await checkOTPStatus()
        return r.data
    }

    async function checkOTPStatus() {
        let r = await axios.get("/api/userProfiles/otp-status/")
        otpStatus.value = r.data;
    }

    return {
        userInfo,
        otpStatus,
        checkLogin,
        login,
        logout,
        verifyOTP,
        checkOTPStatus,
    }
})