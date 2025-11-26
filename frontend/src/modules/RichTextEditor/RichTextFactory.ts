import RichTextQuills from "./RichTextQuills";
import RicheTextInterface from "./RicheTextInterface";

class RichTextFactory {
    

    public static create(HTMLTextAreaElement: HTMLTextAreaElement): RicheTextInterface {
        
        return new RichTextQuills(HTMLTextAreaElement);
    }
}
export default RichTextFactory;