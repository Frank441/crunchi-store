'use client';
import { LoginBox } from './components';

const PageContent = () => {
    return (
        <div className="py-32 w-full flex flex-col justify-center items-center">
            <h1 className="text-white font-ubuntu text-4xl"> Acceder</h1>
            <LoginBox />
        </div>
    )
}

export default PageContent;
