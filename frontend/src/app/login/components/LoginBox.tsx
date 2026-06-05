'use client';
import { InputAdornment, TextField } from '@mui/material';
import { useState} from 'react';

const LoginBox = () => {
    const [passwordInputType, setPasswordInputType] = useState<'password' | 'text'>('password');
    const [buttonDisabled, setButtonDisabled] = useState<boolean>(true);

    const togglePasswordType = () => {
        if (passwordInputType === 'password') setPasswordInputType('text')
        if (passwordInputType === 'text') setPasswordInputType('password')
    }

    const disableButton = () =>{
        return setButtonDisabled(true);
    }

    const enableButton = () => {
        return setButtonDisabled(false)
    }
    const activeStyles = 
    return (
        <form className="w-1/3 mt-8">
            <TextField variant='standard' label="Dirección de email" color='primary' margin='normal' fullWidth />
            <TextField variant='standard' label="Contraseña" type={passwordInputType} color='primary' margin='normal' fullWidth
                slotProps={{
                    input: {
                        endAdornment: (
                            <InputAdornment position='end' onClick={togglePasswordType}>
                                <span className="text-white/60 font-helvetica text-xs uppercase font-bold tracking-wide cursor-pointer hover:text-white/90 transition-colors duration-300">Mostrar</span>
                            </InputAdornment>
                        )

                    }
                }}
            />
            <button className="bg-primary mt-12 w-full text-center py-2 rounded-full cursor-pointer text-bold uppercase text-black hover:bg-primary-hovered transition-all duration-300">Acceder</button>
        </form>
    )
}

export default LoginBox;