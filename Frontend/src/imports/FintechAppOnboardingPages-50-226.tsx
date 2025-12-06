import svgPaths from "./svg-y8vqgn1gnz";
import imgRectangle16 from "figma:asset/974836671650402b605ef1c01e74243e4a51a3cc.png";
import imgImg62862 from "figma:asset/38e23388481c05d1d91ff815e24a983b88386670.png";

function Paragraph() {
  return (
    <div className="h-[143.978px] relative shrink-0 w-full" data-name="Paragraph">
      <div className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[24px] left-[0.23px] not-italic text-[16px] text-white top-[-0.77px] w-[274px]">
        <p className="mb-0">{`Hi! I'm Botl the Axolotl, your AI financial advisor!!`}</p>
        <p className="mb-0">&nbsp;</p>
        <p>You have $84.00 available. Would you like me to suggest which buckets to fill? I want to be swimming in all your buckets of dreams! 🪣</p>
      </div>
    </div>
  );
}

function Container() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] content-stretch flex flex-col h-[220px] items-start left-[80px] pb-[0.771px] pt-[16.769px] px-[16.769px] rounded-bl-[8px] rounded-br-[24px] rounded-tl-[24px] rounded-tr-[24px] top-[104px] w-[300px]" data-name="Container">
      <div aria-hidden="true" className="absolute border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid inset-0 pointer-events-none rounded-bl-[8px] rounded-br-[24px] rounded-tl-[24px] rounded-tr-[24px]" />
      <Paragraph />
    </div>
  );
}

function MaskGroup() {
  return (
    <div className="grid-cols-[max-content] grid-rows-[max-content] inline-grid leading-[0] place-items-start relative shrink-0" data-name="Mask group">
      <div className="[grid-area:1_/_1] bg-white mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[16px] mask-size-[58px_58px] ml-[-16px] mt-[-16px] size-[118px]" style={{ maskImage: `url('${imgRectangle16}')` }} />
      <div className="[grid-area:1_/_1] h-[53.677px] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[-3.172px_-7.25px] mask-size-[58px_58px] ml-[3.17px] mt-[7.25px] relative w-[52.626px]" data-name="IMG_6286 2" style={{ maskImage: `url('${imgRectangle16}')` }}>
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <img alt="" className="absolute h-[109.19%] left-0 max-w-none top-0 w-[104.76%]" src={imgImg62862} />
        </div>
      </div>
    </div>
  );
}

function Heading() {
  return (
    <div className="h-[35.995px] relative shrink-0 w-full" data-name="Heading 1">
      <p className="absolute font-['Momo_Trust_Display:Regular',sans-serif] leading-[36px] left-0 not-italic text-[30px] text-nowrap text-white top-[-0.31px] whitespace-pre">Botl AI</p>
    </div>
  );
}

function Paragraph1() {
  return (
    <div className="h-[19.997px] relative shrink-0 w-full" data-name="Paragraph">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-0 not-italic text-[14px] text-[rgba(255,255,255,0.7)] text-nowrap top-[-0.23px] whitespace-pre">Your financial guide to freedom!</p>
    </div>
  );
}

function Container1() {
  return (
    <div className="content-stretch flex flex-col h-[55.992px] items-start relative shrink-0 w-[140.425px]" data-name="Container">
      <Heading />
      <Paragraph1 />
    </div>
  );
}

function Frame() {
  return (
    <div className="absolute content-stretch flex gap-[12px] items-center left-[10px] top-[18px] w-[370px]">
      <MaskGroup />
      <Container1 />
    </div>
  );
}

function MaskGroup1() {
  return (
    <div className="absolute contents left-[10px] top-[295px]" data-name="Mask group">
      <div className="absolute bg-white left-[-6px] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[16px] mask-size-[58px_58px] size-[118px] top-[279px]" style={{ maskImage: `url('${imgRectangle16}')` }} />
      <div className="absolute h-[53.677px] left-[13.17px] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[-3.172px_-7.25px] mask-size-[58px_58px] top-[302.25px] w-[52.626px]" data-name="IMG_6286 2" style={{ maskImage: `url('${imgRectangle16}')` }}>
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <img alt="" className="absolute h-[109.19%] left-0 max-w-none top-0 w-[104.76%]" src={imgImg62862} />
        </div>
      </div>
    </div>
  );
}

function AiAgent() {
  return (
    <div className="h-[852.69px] relative shrink-0 w-full" data-name="AIAgent">
      <Container />
      <Frame />
      <MaskGroup1 />
    </div>
  );
}

function App() {
  return (
    <div className="absolute bg-gradient-to-b content-stretch flex flex-col from-[#3930f3] h-[980.683px] items-start left-0 overflow-clip to-[#83d6e2] top-0 w-[393.194px]" data-name="App">
      <AiAgent />
    </div>
  );
}

function Paragraph2() {
  return (
    <div className="h-[15.998px] relative shrink-0 w-full" data-name="Paragraph">
      <div className="size-full">
        <div className="content-stretch flex h-[15.998px] items-start px-[8px] py-0 relative w-full">
          <p className="basis-0 font-['Inter:Regular',sans-serif] font-normal grow leading-[16px] min-h-px min-w-px not-italic relative shrink-0 text-[12px] text-[rgba(255,255,255,0.6)]">💡 Try asking:</p>
        </div>
      </div>
    </div>
  );
}

function Button() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid h-[37.536px] left-0 rounded-[2.58694e+07px] top-0 w-[132.257px]" data-name="Button">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-[65.5px] not-italic text-[14px] text-center text-nowrap text-white top-[7.77px] translate-x-[-50%] whitespace-pre">Suggest a split</p>
    </div>
  );
}

function Button1() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid h-[37.536px] left-[140.26px] rounded-[2.58694e+07px] top-0 w-[134.811px]" data-name="Button">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-[67px] not-italic text-[14px] text-center text-nowrap text-white top-[7.77px] translate-x-[-50%] whitespace-pre">Show my goals</p>
    </div>
  );
}

function Button2() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid h-[37.536px] left-[283.07px] rounded-[2.58694e+07px] top-0 w-[109.646px]" data-name="Button">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-[54px] not-italic text-[14px] text-center text-nowrap text-white top-[7.77px] translate-x-[-50%] whitespace-pre">Budget tips</p>
    </div>
  );
}

function Button3() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid h-[37.536px] left-[400.71px] rounded-[2.58694e+07px] top-0 w-[203.499px]" data-name="Button">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-[101px] not-italic text-[14px] text-center text-nowrap text-white top-[7.77px] translate-x-[-50%] whitespace-pre">How much should I save?</p>
    </div>
  );
}

function Button4() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.1)] border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid h-[37.536px] left-[612.21px] rounded-[2.58694e+07px] top-0 w-[160.879px]" data-name="Button">
      <p className="absolute font-['Inter:Regular',sans-serif] font-normal leading-[20px] left-[80px] not-italic text-[14px] text-center text-nowrap text-white top-[7.77px] translate-x-[-50%] whitespace-pre">Track my spending</p>
    </div>
  );
}

function Container2() {
  return (
    <div className="h-[45.535px] overflow-clip relative shrink-0 w-full" data-name="Container">
      <Button />
      <Button1 />
      <Button2 />
      <Button3 />
      <Button4 />
    </div>
  );
}

function Container3() {
  return (
    <div className="content-stretch flex flex-col gap-[7.999px] h-[69.532px] items-start relative shrink-0 w-full" data-name="Container">
      <Paragraph2 />
      <Container2 />
    </div>
  );
}

function TextInput() {
  return (
    <div className="basis-0 grow h-[39.994px] min-h-px min-w-px relative shrink-0" data-name="Text Input">
      <div className="flex flex-row items-center overflow-clip rounded-[inherit] size-full">
        <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex h-[39.994px] items-center px-[16px] py-[8px] relative w-full">
          <p className="font-['Inter:Regular',sans-serif] font-normal leading-[normal] not-italic relative shrink-0 text-[16px] text-[rgba(255,255,255,0.5)] text-nowrap whitespace-pre">Ask Botl anything...</p>
        </div>
      </div>
    </div>
  );
}

function Icon() {
  return (
    <div className="relative shrink-0 size-[19.997px]" data-name="Icon">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 20 20">
        <g clipPath="url(#clip0_50_258)" id="Icon">
          <path d={svgPaths.p3f74af20} id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          <path d={svgPaths.p3e048570} id="Vector_2" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
        </g>
        <defs>
          <clipPath id="clip0_50_258">
            <rect fill="white" height="19.997" width="19.997" />
          </clipPath>
        </defs>
      </svg>
    </div>
  );
}

function Button5() {
  return (
    <div className="bg-[#feff09] opacity-50 relative rounded-[2.58694e+07px] shrink-0 size-[39.994px]" data-name="Button">
      <div className="bg-clip-padding border-0 border-[transparent] border-solid content-stretch flex items-center justify-center relative size-[39.994px]">
        <Icon />
      </div>
    </div>
  );
}

function Container4() {
  return (
    <div className="bg-[rgba(255,255,255,0.2)] h-[57.533px] relative rounded-[2.58694e+07px] shrink-0 w-full" data-name="Container">
      <div aria-hidden="true" className="absolute border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid inset-0 pointer-events-none rounded-[2.58694e+07px]" />
      <div className="size-full">
        <div className="content-stretch flex gap-[7.999px] h-[57.533px] items-start pb-[0.771px] pt-[8.77px] px-[8.77px] relative w-full">
          <TextInput />
          <Button5 />
        </div>
      </div>
    </div>
  );
}

function AiAgent1() {
  return (
    <div className="absolute content-stretch flex flex-col gap-[11.998px] h-[139.063px] items-start left-0 px-[23.996px] py-0 top-[633.63px] w-[393.194px]" data-name="AIAgent">
      <Container3 />
      <Container4 />
    </div>
  );
}

function Icon1() {
  return (
    <div className="h-[19.997px] overflow-clip relative shrink-0 w-full" data-name="Icon">
      <div className="absolute bottom-[12.5%] left-[37.5%] right-[37.5%] top-1/2" data-name="Vector">
        <div className="absolute inset-[-11.11%_-16.67%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 7 10">
            <path d={svgPaths.pc8d3280} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[8.33%_12.5%_12.5%_12.5%]" data-name="Vector">
        <div className="absolute inset-[-5.26%_-5.56%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 17 18">
            <path d={svgPaths.p659df00} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Button6() {
  return (
    <div className="absolute content-stretch flex flex-col h-[35.995px] items-start left-0 pb-0 pt-[7.999px] px-[15.998px] rounded-[2.58694e+07px] top-0 w-[51.992px]" data-name="Button">
      <Icon1 />
    </div>
  );
}

function Icon2() {
  return (
    <div className="h-[19.997px] overflow-clip relative shrink-0 w-full" data-name="Icon">
      <div className="absolute inset-[12.5%_66.67%_54.17%_16.67%]" data-name="Vector">
        <div className="absolute inset-[-12.5%_-25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 5 9">
            <path d={svgPaths.p2f79fd80} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[29.17%_16.67%_70.83%_16.67%]" data-name="Vector">
        <div className="absolute inset-[-0.83px_-6.25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 15 2">
            <path d="M0.833207 0.833207H14.1645" id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[54.17%_16.67%_12.5%_66.67%]" data-name="Vector">
        <div className="absolute inset-[-12.5%_-25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 5 9">
            <path d={svgPaths.p3ac933c0} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[70.83%_16.67%_29.17%_16.67%]" data-name="Vector">
        <div className="absolute inset-[-0.83px_-6.25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 15 2">
            <path d="M14.1645 0.833207H0.833207" id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Button7() {
  return (
    <div className="absolute content-stretch flex flex-col h-[35.995px] items-start left-[59.99px] pb-0 pt-[7.999px] px-[15.998px] rounded-[2.58694e+07px] top-0 w-[51.992px]" data-name="Button">
      <Icon2 />
    </div>
  );
}

function Icon3() {
  return (
    <div className="h-[19.997px] overflow-clip relative shrink-0 w-full" data-name="Icon">
      <div className="absolute inset-[12.5%_8.33%_33.33%_12.5%]" data-name="Vector">
        <div className="absolute inset-[-7.69%_-5.26%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 18 13">
            <path d={svgPaths.p27074780} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[20.83%_12.5%_12.5%_12.5%]" data-name="Vector">
        <div className="absolute inset-[-6.25%_-5.56%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 17 15">
            <path d={svgPaths.p13980100} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Button8() {
  return (
    <div className="absolute content-stretch flex flex-col h-[35.995px] items-start left-[119.98px] pb-0 pt-[7.999px] px-[15.998px] rounded-[2.58694e+07px] top-0 w-[51.992px]" data-name="Button">
      <Icon3 />
    </div>
  );
}

function Icon4() {
  return (
    <div className="h-[19.997px] overflow-clip relative shrink-0 w-full" data-name="Icon">
      <div className="absolute bottom-[66.67%] left-[33.33%] right-1/2 top-[16.67%]" data-name="Vector">
        <div className="absolute inset-[-25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 5 5">
            <path d={svgPaths.p3b615c80} id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[33.33%_16.67%_16.67%_16.67%]" data-name="Vector">
        <div className="absolute inset-[-8.33%_-6.25%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 15 12">
            <path d={svgPaths.pbe4f80} id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[58.33%_83.33%_41.67%_8.33%]" data-name="Vector">
        <div className="absolute inset-[-0.83px_-50%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 4 2">
            <path d="M0.833207 0.833207H2.49962" id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[58.33%_8.33%_41.67%_83.33%]" data-name="Vector">
        <div className="absolute inset-[-0.83px_-50%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 4 2">
            <path d="M0.833207 0.833207H2.49962" id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[54.17%_37.5%_37.5%_62.5%]" data-name="Vector">
        <div className="absolute inset-[-50%_-0.83px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 2 4">
            <path d="M0.833207 0.833207V2.49962" id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[54.17%_62.5%_37.5%_37.5%]" data-name="Vector">
        <div className="absolute inset-[-50%_-0.83px]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 2 4">
            <path d="M0.833207 0.833207V2.49962" id="Vector" stroke="var(--stroke-0, #0F172A)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Button9() {
  return (
    <div className="absolute bg-[#feff09] content-stretch flex flex-col h-[35.995px] items-start left-[179.97px] pb-0 pt-[7.999px] px-[15.998px] rounded-[2.58694e+07px] top-0 w-[51.992px]" data-name="Button">
      <Icon4 />
    </div>
  );
}

function Icon5() {
  return (
    <div className="h-[19.997px] overflow-clip relative shrink-0 w-full" data-name="Icon">
      <div className="absolute inset-[62.5%_20.83%_12.5%_20.83%]" data-name="Vector">
        <div className="absolute inset-[-16.67%_-7.14%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 14 7">
            <path d={svgPaths.p6506980} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
      <div className="absolute inset-[12.5%_33.33%_54.17%_33.33%]" data-name="Vector">
        <div className="absolute inset-[-12.5%]">
          <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 9 9">
            <path d={svgPaths.p1d0f7ec0} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.66641" />
          </svg>
        </div>
      </div>
    </div>
  );
}

function Button10() {
  return (
    <div className="absolute content-stretch flex flex-col h-[35.995px] items-start left-[239.96px] pb-0 pt-[7.999px] px-[15.998px] rounded-[2.58694e+07px] top-0 w-[51.992px]" data-name="Button">
      <Icon5 />
    </div>
  );
}

function Container5() {
  return (
    <div className="h-[35.995px] relative shrink-0 w-full" data-name="Container">
      <Button6 />
      <Button7 />
      <Button8 />
      <Button9 />
      <Button10 />
    </div>
  );
}

function App1() {
  return (
    <div className="absolute bg-[rgba(255,255,255,0.2)] content-stretch flex flex-col h-[61.533px] items-start left-[25.85px] pb-[0.771px] pt-[12.769px] px-[24.767px] rounded-[2.58694e+07px] top-[767.16px] w-[341.491px]" data-name="App">
      <div aria-hidden="true" className="absolute border-[0.771px] border-[rgba(255,255,255,0.2)] border-solid inset-0 pointer-events-none rounded-[2.58694e+07px] shadow-[0px_25px_50px_-12px_rgba(0,0,0,0.25)]" />
      <Container5 />
    </div>
  );
}

export default function FintechAppOnboardingPages() {
  return (
    <div className="bg-white relative size-full" data-name="Fintech App Onboarding Pages">
      <App />
      <AiAgent1 />
      <App1 />
    </div>
  );
}