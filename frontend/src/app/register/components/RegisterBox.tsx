'use client';
import { InputAdornment, TextField } from '@mui/material';
import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useRegister } from '@/hooks/useRegister';
import { useRouter } from 'next/navigation';

interface RegisterFormInputs {
    alias: string;
    email: string;
    password: string;
}

const RegisterBox = () => {
    const [passwordInputType, setPasswordInputType] = useState<'password' | 'text'>('password');
    const { register, isLoading, isRegistered, errors: apiError } = useRegister();
    const { push } = useRouter();
    const { handleSubmit, control, watch, formState: { errors } } = useForm<RegisterFormInputs>({
        defaultValues: { alias: '', email: '', password: '' },
        mode: 'onChange'
    });

    const alias = watch('alias');
    const email = watch('email');
    const password = watch('password');
    const isButtonEnabled = !errors.alias && !errors.email && !errors.password && alias && email && password;

    const togglePasswordType = () => {
        setPasswordInputType(prev => prev === 'password' ? 'text' : 'password');
    };

    const disabledClasses = 'bg-transparent border-4 border-red/30 text-gray/30 cursor-not-allowed';
    const enabledClasses = 'bg-primary text-black cursor-pointer hover:bg-primary-hovered';

    useEffect(() => {
        if (isRegistered) push('/home');
    }, [isRegistered, push]);

    return (
        <form className="w-1/3 mt-8" onSubmit={handleSubmit(values => {
            register(values.email, values.password, values.alias)
        })}>
            <Controller
                name="alias"
                control={control}
                rules={{
                    required: 'El alias es requerido',
                    minLength: {
                        value: 1,
                        message: 'El alias no puede estar vacío'
                    }
                }}
                render={({ field }) => (
                    <TextField
                        {...field}
                        variant='standard'
                        label="Alias"
                        color='primary'
                        margin='normal'
                        fullWidth
                        error={!!errors.alias}
                        helperText={errors.alias?.message}
                    />
                )}
            />
            <Controller
                name="email"
                control={control}
                rules={{
                    required: 'El email es requerido',
                    pattern: {
                        value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                        message: 'Email inválido'
                    }
                }}
                render={({ field }) => (
                    <TextField
                        {...field}
                        variant='standard'
                        label="Dirección de email"
                        color='primary'
                        margin='normal'
                        fullWidth
                        error={!!errors.email}
                        helperText={errors.email?.message}
                    />
                )}
            />
            <Controller
                name="password"
                control={control}
                rules={{
                    required: 'La contraseña es requerida',
                    minLength: {
                        value: 6,
                        message: 'Mínimo 6 caracteres'
                    }
                }}
                render={({ field }) => (
                    <TextField
                        {...field}
                        variant='standard'
                        label="Contraseña"
                        type={passwordInputType}
                        color='primary'
                        margin='normal'
                        fullWidth
                        error={!!errors.password}
                        helperText={errors.password?.message}
                        slotProps={{
                            input: {
                                endAdornment: (
                                    <InputAdornment position='end' onClick={togglePasswordType}>
                                        <span className="text-white/60 font-helvetica text-xs uppercase font-bold tracking-wide hover:text-white/90 transition-colors duration-300">Mostrar</span>
                                    </InputAdornment>
                                )
                            }
                        }}
                    />
                )}
            />
            {apiError && (
                <p className="mt-4 text-red-400 font-helvetica text-sm">{apiError}</p>
            )}
            <button
                disabled={!isButtonEnabled || isLoading}
                className={`mt-12 w-full text-center py-2 rounded-full text-bold uppercase transition-all duration-300 ${isButtonEnabled ? enabledClasses : disabledClasses}`}
            >
                {!isLoading ? 'Crear cuenta' : 'Cargando...'}
            </button>
        </form>
    );
};

export default RegisterBox;
